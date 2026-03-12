def get_all_rows(service, spreadsheet_id, tab_name):
    try:
        result = service.spreadsheets().values().get(
            spreadsheetId=spreadsheet_id,
            range=f"{tab_name}!A:Z"
        ).execute()
        return result.get('values', [])
    except Exception as e:
        if "Unable to parse range" in str(e) or "not found" in str(e).lower():
            return []
        raise e

def ensure_sheet_exists(service, spreadsheet_id, tab_name):
    """Check if a sheet tab exists, if not create it"""
    try:
        spreadsheet = service.spreadsheets().get(spreadsheetId=spreadsheet_id).execute()
        existing_tabs = [s.get('properties', {}).get('title') for s in spreadsheet.get('sheets', [])]
        
        if tab_name not in existing_tabs:
            print(f"    Creating new sheet: {tab_name}")
            requests = [{
                "addSheet": {
                    "properties": {
                        "title": tab_name
                    }
                }
            }]
            body = {"requests": requests}
            service.spreadsheets().batchUpdate(spreadsheetId=spreadsheet_id, body=body).execute()
            print(f"    Created sheet: {tab_name}")
        return True
    except Exception as e:
        print(f"    Warning: Could not check/create sheet: {e}")
        return False

def write_rows(service, spreadsheet_id, tab_name, rows):
    service.spreadsheets().values().update(
        spreadsheetId=spreadsheet_id,
        range=f"{tab_name}!A1",
        body={
            'values': rows
        },
        valueInputOption='USER_ENTERED'
    ).execute()

def write_status_only(service, spreadsheet_id, tab_name, row_updates):
    for row_num, status in row_updates:
        range_str = f"{tab_name}!J{row_num}"
        service.spreadsheets().values().update(
            spreadsheetId=spreadsheet_id,
            range=range_str,
            body={'values': [[status]]},
            valueInputOption='USER_ENTERED'
        ).execute()

def append_rows(service, spreadsheet_id, tab_name, rows):
    result = service.spreadsheets().values().get(
        spreadsheetId=spreadsheet_id,
        range=f"{tab_name}!A1"
    ).execute()
    
    last_row = len(result.get('values', [])) + 1
    
    service.spreadsheets().values().update(
        spreadsheetId=spreadsheet_id,
        range=f"{tab_name}!A{last_row}",
        body={
            'values': rows
        },
        valueInputOption='USER_ENTERED'
    ).execute()

def clear_tab(service, spreadsheet_id, tab_name):
    service.spreadsheets().values().clear(
        spreadsheetId=spreadsheet_id,
        range=f"{tab_name}!A:Z"
    ).execute()

TYPE_COLORS = {
    'Promotions': {'red': 1.0, 'green': 0.8, 'blue': 0.8},
    'Newsletters': {'red': 0.8, 'green': 0.9, 'blue': 1.0},
    'Receipts': {'red': 0.8, 'green': 1.0, 'blue': 0.8},
    'Payments': {'red': 1.0, 'green': 0.9, 'blue': 0.7},
    'Job': {'red': 0.9, 'green': 0.8, 'blue': 1.0},
    'Personal': {'red': 0.9, 'green': 1.0, 'blue': 0.9},
    'Unknown': {'red': 0.95, 'green': 0.95, 'blue': 0.95}
}

AI_COLORS = {
    'Promotions': {'red': 0.95, 'green': 0.6, 'blue': 0.6},   # Light Red
    'Social': {'red': 0.6, 'green': 0.7, 'blue': 0.95},        # Light Blue
    'Receipts': {'red': 0.6, 'green': 0.85, 'blue': 0.6},     # Light Green
    'Payments': {'red': 0.95, 'green': 0.75, 'blue': 0.5},    # Light Orange
    'Job': {'red': 0.8, 'green': 0.6, 'blue': 0.9},           # Light Purple
    'Personal': {'red': 0.6, 'green': 0.85, 'blue': 0.8},     # Light Teal
    'Updates': {'red': 0.95, 'green': 0.95, 'blue': 0.6},     # Light Yellow
    'Travel': {'red': 0.7, 'green': 0.8, 'blue': 0.95},      # Light Indigo
    'Unknown': {'red': 0.85, 'green': 0.85, 'blue': 0.85}     # Light Gray
}

def format_senders_tab(service, spreadsheet_id, tab_name, num_rows, ai_suggestions=None):
    try:
        spreadsheet = service.spreadsheets().get(spreadsheetId=spreadsheet_id).execute()
        sheet_id = None
        for sheet in spreadsheet.get('sheets', []):
            if sheet.get('properties', {}).get('title') == tab_name:
                sheet_id = sheet.get('properties', {}).get('sheetId')
                break
        
        if sheet_id is None:
            return
        
        requests = []
        
        requests.append({
            "repeatCell": {
                "range": {
                    "sheetId": sheet_id,
                    "startRowIndex": 0,
                    "endRowIndex": 1,
                    "startColumnIndex": 0,
                    "endColumnIndex": 10
                },
                "cell": {
                    "userEnteredFormat": {
                        "backgroundColor": {"red": 0.13, "green": 0.29, "blue": 0.53},
                        "textFormat": {"bold": True, "foregroundColor": {"red": 1, "green": 1, "blue": 1}},
                        "horizontalAlignment": "CENTER"
                    }
                },
                "fields": "userEnteredFormat(backgroundColor,textFormat,horizontalAlignment)"
            }
        })
        
        if num_rows > 1:
            requests.append({
                "repeatCell": {
                    "range": {
                        "sheetId": sheet_id,
                        "startRowIndex": 1,
                        "endRowIndex": num_rows,
                        "startColumnIndex": 0,
                        "endColumnIndex": 10
                    },
                    "cell": {
                        "userEnteredFormat": {
                            "borders": {
                                "top": {"style": "SOLID", "color": {"red": 0.9, "green": 0.9, "blue": 0.9}},
                                "bottom": {"style": "SOLID", "color": {"red": 0.9, "green": 0.9, "blue": 0.9}},
                                "left": {"style": "SOLID", "color": {"red": 0.9, "green": 0.9, "blue": 0.9}},
                                "right": {"style": "SOLID", "color": {"red": 0.9, "green": 0.9, "blue": 0.9}}
                            }
                        }
                    },
                    "fields": "userEnteredFormat(borders)"
                }
            })
            
            if ai_suggestions:
                for i, ai_type in enumerate(ai_suggestions):
                    if ai_type in AI_COLORS and i + 2 <= num_rows:
                        color = AI_COLORS[ai_type]
                        requests.append({
                            "repeatCell": {
                                "range": {
                                    "sheetId": sheet_id,
                                    "startRowIndex": i + 2,
                                    "endRowIndex": i + 3,
                                    "startColumnIndex": 6,
                                    "endColumnIndex": 7
                                },
                                "cell": {
                                    "userEnteredFormat": {
                                        "backgroundColor": color,
                                        "textFormat": {"bold": True}
                                    }
                                },
                                "fields": "userEnteredFormat(backgroundColor,textFormat)"
                            }
                        })
        
        body = {"requests": requests}
        service.spreadsheets().batchUpdate(spreadsheetId=spreadsheet_id, body=body).execute()
    except Exception as e:
        print(f"Warning: Could not format sheet: {e}")

def add_dropdown_validation(service, spreadsheet_id, tab_name, column_index=8, num_rows=100):
    try:
        spreadsheet = service.spreadsheets().get(spreadsheetId=spreadsheet_id).execute()
        sheet_id = None
        for sheet in spreadsheet.get('sheets', []):
            if sheet.get('properties', {}).get('title') == tab_name:
                sheet_id = sheet.get('properties', {}).get('sheetId')
                break
        
        if sheet_id is None:
            return
        
        requests = [{
            "setDataValidation": {
                "range": {
                    "sheetId": sheet_id,
                    "startRowIndex": 1,
                    "endRowIndex": num_rows,
                    "startColumnIndex": column_index,
                    "endColumnIndex": column_index + 1
                },
                "rule": {
                    "condition": {
                        "type": "ONE_OF_LIST",
                        "values": [
                            {"userEnteredValue": ""},
                            {"userEnteredValue": "Keep"},
                            {"userEnteredValue": "Label Only"},
                            {"userEnteredValue": "Trash Backlog"},
                            {"userEnteredValue": "Trash All"}
                        ]
                    },
                    "showCustomUi": True,
                    "strict": False
                }
            }
        }]
        
        body = {"requests": requests}
        service.spreadsheets().batchUpdate(spreadsheetId=spreadsheet_id, body=body).execute()
    except Exception as e:
        print(f"Warning: Could not add dropdown: {e}")

def create_instructions_tab(service, spreadsheet_id):
    try:
        spreadsheet = service.spreadsheets().get(spreadsheetId=spreadsheet_id).execute()
        existing_tabs = [s.get('properties', {}).get('title') for s in spreadsheet.get('sheets', [])]
        
        sheet_id_to_delete = None
        for sheet in spreadsheet.get('sheets', []):
            if sheet.get('properties', {}).get('title') == 'Emails':
                sheet_id_to_delete = sheet.get('properties', {}).get('sheetId')
        
        requests = []
        
        if sheet_id_to_delete:
            requests.append({
                "deleteSheet": {
                    "sheetId": sheet_id_to_delete
                }
            })
        
        if 'Instructions' not in existing_tabs:
            requests.append({
                "addSheet": {
                    "properties": {
                        "title": "Instructions"
                    }
                }
            })
        
        if requests:
            body = {"requests": requests}
            service.spreadsheets().batchUpdate(spreadsheetId=spreadsheet_id, body=body).execute()
        
        instructions_content = [
            ["GMAIL ORGANISER v3 - INSTRUCTIONS"],
            [""],
            ["HOW IT WORKS:"],
            ["1. This tool scans your Gmail and groups emails by sender"],
            ["2. It uses AI (Hugging Face) to classify emails automatically"],
            ["3. First scan captures ALL emails (no limit)"],
            ["4. Subsequent scans only fetch NEW emails (incremental)"],
            ["5. You select an action from the dropdown in 'human_decision' column"],
            ["6. Click 'Apply Decisions' to execute your choices"],
            [""],
            ["STREAMLIT APP:"],
            ["Run: streamlit run src/app.py"],
            ["Then use the buttons in the browser to Scan or Apply"],
            [""],
            ["COLUMN DESCRIPTIONS:"],
            ["A: from_email", "The sender's email address"],
            ["B: sender", "The sender's display name"],
            ["C: total_messages", "Number of messages from this sender"],
            ["D: sample_subjects", "Sample email subjects for identification"],
            ["E: gmail_category", "Gmail's built-in category (Primary, Promotions, Social, Updates)"],
            ["F: has_unsubscribe", "TRUE if the sender includes an unsubscribe link"],
            ["G: ai_suggestion", "AI Classification - Color coded (see legend below)"],
            ["H: deleted_count", "Total emails from this sender trashed (lifetime counter)"],
            ["I: human_decision", "YOUR decision - select from the dropdown"],
            ["J: status", "pending = needs decision, done = action applied"],
            [""],
            ["DECISION OPTIONS:"],
            ["Keep", "Do nothing - leave emails as is"],
            ["Label Only", "Add the nested AO/ label but don't trash"],
            ["Trash Backlog", "Trash emails older than 90 days"],
            ["Trash All", "Trash ALL emails from this sender"],
            [""],
            ["LABEL LEGEND:"],
            ["AO/Promotions", "Marketing, newsletters, promotional emails"],
            ["AO/Receipts", "Order confirmations, invoices"],
            ["AO/Payments", "Billing, subscriptions"],
            ["AO/Job", "Job applications, interview notifications"],
            ["AO/Personal", "Personal emails, friends, family"],
            ["AO/ReviewQueue", "Uncategorized - needs manual review"],
            [""],
            ["AI SUGGESTION COLOR LEGEND:"],
            ["Promotions", "Light Red"],
            ["Social", "Light Blue"],
            ["Receipts", "Light Green"],
            ["Payments", "Light Orange"],
            ["Job", "Light Purple"],
            ["Personal", "Light Teal"],
            ["Updates", "Light Yellow"],
            ["Travel", "Light Indigo"],
            ["Unknown", "Light Gray"],
            [""],
            ["SAFETY RULES:"],
            ["- Starred emails are NEVER trashed"],
            ["- Primary + Starred emails are NEVER trashed"],
            [""],
            ["CLASSIFIER:"],
            ["This tool uses enhanced keyword-based classification"],
            ["Analyzes email subjects and snippets to predict categories"],
        ]
        
        service.spreadsheets().values().update(
            spreadsheetId=spreadsheet_id,
            range="Instructions!A1",
            body={'values': instructions_content},
            valueInputOption='USER_ENTERED'
        ).execute()
    except Exception as e:
        print(f"Warning: Could not create instructions tab: {e}")
