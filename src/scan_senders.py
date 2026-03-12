import yaml
import json
import os
from collections import defaultdict
from datetime import datetime

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
CONFIG_FILE = os.path.join(BASE_DIR, 'config.yaml')
STATE_FILE = os.path.join(BASE_DIR, 'state.json')

from src.auth import get_gmail_service, get_sheets_service
from src.gmail_client import list_message_ids, get_message_metadata, modify_labels, trash_message, create_label, delete_labels_with_prefix
from src.sheets_client import get_all_rows, write_rows, format_senders_tab, add_dropdown_validation, create_instructions_tab, ensure_sheet_exists
from src.classify_senders import classify_sender
from src.ai_classifier import classify_sender_ai

def load_state():
    if os.path.exists(STATE_FILE):
        with open(STATE_FILE, 'r') as f:
            return json.load(f)
    return {'last_scan_timestamp': None}

def save_state(timestamp):
    with open(STATE_FILE, 'w') as f:
        json.dump({'last_scan_timestamp': timestamp}, f)

def run_scan_senders(force_full_scan=False, clean_old_labels=False, progress_callback=None):
    def report_progress(pct, message):
        if progress_callback:
            progress_callback(min(pct, 100), message)

    with open(CONFIG_FILE, 'r') as f:
        config = yaml.safe_load(f)
    
    gmail_cfg = config['gmail']
    sheets_cfg = config['sheets']
    
    state = load_state()
    last_timestamp = state.get('last_scan_timestamp')
    
    gmail_service = get_gmail_service()
    sheets_service = get_sheets_service()
    
    if clean_old_labels:
        report_progress(5, "Cleaning old labels...")
        delete_labels_with_prefix(gmail_service, gmail_cfg.get('label_namespace', 'AO/'))
    
    report_progress(10, "Ensuring Senders sheet exists...")
    ensure_sheet_exists(sheets_service, sheets_cfg['spreadsheet_id'], sheets_cfg['tabs']['senders'])
    
    search_query = gmail_cfg['search_query']
    if not force_full_scan and last_timestamp:
        search_query = f"in:anywhere after:{last_timestamp}"
    
    report_progress(20, "Fetching message IDs...")
    message_ids = list_message_ids(gmail_service, query=search_query, max_results=gmail_cfg.get('max_results', 100))
    
    if not message_ids:
        return {'success': True, 'messages': 0, 'senders': 0}

    messages_metadata = []
    for msg_info in message_ids:
        metadata = get_message_metadata(gmail_service, msg_id=msg_info['id'])
        if metadata and metadata.get('from_email'):
            messages_metadata.append(metadata)
    
    print(f"Fetched {len(messages_metadata)} emails")

    grouped = defaultdict(list)
    for msg in messages_metadata:
        grouped[msg['from_email']].append(msg)
    
    sender_list = list(grouped.keys())
    sender_data = {}

    for sender in sender_list:
        msgs = grouped[sender]
        classified = classify_sender(msgs)
        if classified:
            subjects = [m.get('subject', '') for m in msgs]
            snippets = [m.get('snippet', '') for m in msgs]
            classified['ai_suggestion'] = classify_sender_ai(subjects, snippets)
            sender_data[sender] = classified
    
    print(f"Classified {len(sender_data)} senders")

    # Get existing rows to preserve decisions
    existing_rows = get_all_rows(sheets_service, sheets_cfg['spreadsheet_id'], sheets_cfg['tabs']['senders'])
    existing_by_email = {row[0]: row for row in existing_rows[1:] if row and len(row) > 0}
    
    headers = ['from_email', 'sender', 'total_messages', 'sample_subjects', 'gmail_category', 'has_unsubscribe', 'ai_suggestion', 'deleted_count', 'human_decision', 'status']
    output_rows = [headers]
    
    for sender, data in sender_data.items():
        row = [
            sender, data.get('sender_name', ''), data.get('count', 0),
            ", ".join(data.get('subjects', [])[:3]), data.get('category', 'Unknown'),
            "Yes" if data.get('has_unsubscribe') else "No", data.get('ai_suggestion', 'Keep'),
            existing_by_email.get(sender, [0]*10)[7] if sender in existing_by_email else 0,
            existing_by_email.get(sender, [0]*10)[8] if sender in existing_by_email else '',
            'pending'
        ]
        output_rows.append(row)

    write_rows(sheets_service, sheets_cfg['spreadsheet_id'], sheets_cfg['tabs']['senders'], output_rows)
    
    # Save state
    new_timestamp = datetime.now().strftime('%Y/%m/%d')
    save_state(new_timestamp)
    
    report_progress(100, "Scan Complete!")
    return {'success': True, 'messages': len(messages_metadata), 'senders': len(sender_data)}
