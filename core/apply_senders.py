import yaml
import os
from datetime import datetime

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
CONFIG_FILE = os.path.join(BASE_DIR, 'config.yaml')

from app.auth import get_gmail_service, get_sheets_service
from app.gmail_client import list_message_ids, get_message_metadata, modify_labels, trash_message, create_label
from app.sheets_client import get_all_rows, write_status_only

TYPE_TO_LABEL = {
    'Promotions': 'AO/Promotions',
    'Newsletters': 'AO/Newsletters',
    'Receipts': 'AO/Receipts',
    'Payments': 'AO/Payments',
    'Job': 'AO/Job',
    'Personal': 'AO/Personal',
    'Unknown': 'AO/ReviewQueue',
    'Social': 'AO/Promotions'
}

def parse_gmail_date(date_str):
    formats = [
        '%a, %d %b %Y %H:%M:%S %z',
        '%d %b %Y %H:%M:%S %z',
        '%Y-%m-%dT%H:%M:%SZ',
    ]
    for fmt in formats:
        try:
            return datetime.strptime(date_str, fmt)
        except ValueError:
            continue
    return None

def apply_decision(service, config, sender, suggested_type, decision):
    label_namespace = config['gmail']['label_namespace']
    delete_older_than_days = config['gmail']['delete_older_than_days']
    protect_starred = config['safety']['protect_starred']
    protect_primary_starred = config['safety']['protect_primary_starred']
    
    gmail_label_id = None
    
    if decision == 'Label Only':
        sender_name = sender.split('@')[0] if '@' in sender else sender
        sender_name = ''.join(c for c in sender_name if c.isalnum())
        sender_name = sender_name.title()
        
        parent_label = TYPE_TO_LABEL.get(suggested_type, label_namespace + 'ReviewQueue')
        create_label(service, label_name=parent_label)
        
        full_label_name = f"{parent_label}/{sender_name}"
        create_label(service, label_name=full_label_name)
        
        labels = service.users().labels().list(userId='me').execute()
        for lbl in labels.get('labels', []):
            if lbl['name'] == full_label_name:
                gmail_label_id = lbl['id']
                break
        
        if not gmail_label_id:
            print(f"    Could not find/create label: {full_label_name}")
            return {'trashed': 0, 'labeled': 0}
    elif decision in ['Trash Backlog', 'Trash All']:
        pass
    else:
        return {'trashed': 0, 'labeled': 0}
    
    max_to_process = 50 if 'Trash All' not in decision else 100
    search_query = f"from:{sender}"
    message_ids = list_message_ids(service, query=search_query, max_results=max_to_process)
    
    print(f"    Found {len(message_ids)} messages from {sender}")
    
    trashed_count = 0
    labeled_count = 0
    
    for msg_info in message_ids:
        metadata = get_message_metadata(service, msg_id=msg_info['id'])
        if not metadata:
            continue
        
        label_ids = metadata.get('gmail_labels', [])
        is_starred = 'STARRED' in label_ids
        is_primary = 'CATEGORY_PRIMARY' in label_ids
        
        should_protect = False
        if protect_starred and is_starred:
            should_protect = True
        if protect_primary_starred and is_starred and is_primary:
            should_protect = True
        
        if should_protect:
            continue
        
        msg_date = parse_gmail_date(metadata.get('date', ''))
        is_old = False
        if msg_date:
            try:
                age = datetime.now(msg_date.tzinfo) - msg_date
                is_old = age.days > delete_older_than_days
            except:
                pass
        
        if decision == 'Keep':
            pass
        elif decision == 'Label Only':
            modify_labels(service, msg_id=msg_info['id'], add_labels=[gmail_label_id])
            labeled_count += 1
        elif decision == 'Trash Backlog':
            if is_old:
                trash_message(service, msg_id=msg_info['id'])
                trashed_count += 1
        elif decision == 'Trash All':
            trash_message(service, msg_id=msg_info['id'])
            trashed_count += 1
    
    return {'trashed': trashed_count, 'labeled': labeled_count}

def run_apply_senders(progress_callback=None):
    def report_progress(step, total, message):
        if progress_callback:
            percent = int((step / total) * 100)
            progress_callback(percent, message)
    
    with open(CONFIG_FILE, 'r') as f:
        config = yaml.safe_load(f)
    
    sheets_cfg = config['sheets']
    
    print("=" * 50)
    print("Starting Apply Decisions...")
    print("=" * 50)
    
    report_progress(1, 10, "Connecting to services...")
    gmail_service = get_gmail_service()
    sheets_service = get_sheets_service()
    
    report_progress(2, 10, "Reading spreadsheet...")
    rows = get_all_rows(
        sheets_service,
        sheets_cfg['spreadsheet_id'],
        sheets_cfg['tabs']['senders']
    )
    
    if len(rows) < 2:
        print("No data found in Senders tab.")
        return {'success': True, 'processed': 0, 'trashed': 0, 'labeled': 0}
    
    headers = rows[0]
    
    pending_rows = []
    for i, row in enumerate(rows[1:], start=2):
        if len(row) < 10:
            row.extend([''] * (10 - len(row)))
        
        from_email = row[0]
        ai_suggestion = row[6] if len(row) > 6 else ''
        human_decision = row[8] if len(row) > 8 else ''
        status = row[9] if len(row) > 9 else ''
        
        if status != 'done' and human_decision:
            pending_rows.append((i, row, from_email, ai_suggestion, human_decision))
    
    if not pending_rows:
        print("No pending decisions to apply.")
        return {'success': True, 'processed': 0, 'trashed': 0, 'labeled': 0}
    
    total_rows = len(pending_rows)
    processed_count = 0
    total_trashed = 0
    total_labeled = 0
    row_updates = []
    
    report_progress(3, 10, f"Processing {total_rows} senders...")
    
    for idx, (row_num, row, from_email, ai_suggestion, human_decision) in enumerate(pending_rows):
        print(f"\nProcessing: {from_email}")
        print(f"    Decision: {human_decision}")
        
        result = apply_decision(
            gmail_service,
            config,
            from_email,
            ai_suggestion,
            human_decision
        )
        
        trashed = result.get('trashed', 0)
        labeled = result.get('labeled', 0)
        
        row_updates.append((row_num, 'done'))
        
        if trashed > 0:
            current_deleted = int(row[7]) if row[7] and row[7].isdigit() else 0
            new_deleted = current_deleted + trashed
            write_deleted_count(sheets_service, sheets_cfg['spreadsheet_id'], sheets_cfg['tabs']['senders'], row_num, new_deleted)
        
        processed_count += 1
        total_trashed += trashed
        total_labeled += labeled
        
        pct = 3 + int(((idx + 1) / total_rows) * 6)
        report_progress(pct, 10, f"Processing... {idx+1}/{total_rows}")
    
    if row_updates:
        report_progress(9, 10, "Updating spreadsheet...")
        print(f"\nUpdating status in sheet...")
        write_status_only(sheets_service, sheets_cfg['spreadsheet_id'], sheets_cfg['tabs']['senders'], row_updates)
    
    report_progress(10, 10, "Complete!")
    
    print("\n" + "=" * 50)
    print(f"APPLY COMPLETE!")
    print(f"  Senders Processed: {processed_count}")
    print(f"  Emails Trashed: {total_trashed}")
    print(f"  Emails Labeled: {total_labeled}")
    print("=" * 50)
    
    return {
        'success': True,
        'processed': processed_count,
        'trashed': total_trashed,
        'labeled': total_labeled
    }

def write_deleted_count(service, spreadsheet_id, tab_name, row_num, count):
    range_str = f"{tab_name}!H{row_num}"
    service.spreadsheets().values().update(
        spreadsheetId=spreadsheet_id,
        range=range_str,
        body={'values': [[str(count)]]},
        valueInputOption='USER_ENTERED'
    ).execute()
