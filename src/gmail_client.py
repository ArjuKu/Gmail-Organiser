from email.utils import parseaddr

def list_message_ids(service, user_id='me', query='', max_results=None):
    results = []
    page_token = None
    
    while True:
        params = {
            'userId': user_id,
            'q': query,
            'maxResults': max_results if max_results else 500
        }
        if page_token:
            params['pageToken'] = page_token
            
        response = service.users().messages().list(**params).execute()
        msgs = response.get('messages', [])
        results.extend(msgs)
        
        page_token = response.get('nextPageToken')
        if not page_token or (max_results and len(results) >= max_results):
            break
    
    return results[:max_results] if max_results else results

def get_message_metadata(service, user_id='me', msg_id=None):
    if msg_id is None:
        return None
    
    msg = service.users().messages().get(
        userId=user_id,
        id=msg_id,
        format='metadata',
        metadataHeaders=['From', 'Subject', 'Date', 'List-Unsubscribe']
    ).execute()
    
    headers = msg.get('payload', {}).get('headers', [])
    header_dict = {h['name'].lower(): h['value'] for h in headers}
    
    from_email = parseaddr(header_dict.get('from', ''))[1]
    from_name = parseaddr(header_dict.get('from', ''))[0]
    
    label_ids = msg.get('labelIds', [])
    gmail_categories = [l for l in label_ids if l.startswith('CATEGORY_')]
    
    return {
        'message_id': msg['id'],
        'thread_id': msg.get('threadId'),
        'date': header_dict.get('date', ''),
        'from_email': from_email,
        'from_name': from_name,
        'subject': header_dict.get('subject', '(No Subject)'),
        'snippet': msg.get('snippet', ''),
        'gmail_labels': label_ids,
        'gmail_category': gmail_categories[0] if gmail_categories else 'CATEGORY_UNDEFINED',
        'has_unsubscribe': 'List-Unsubscribe' in header_dict or any(
            l for l in label_ids if 'UNSUBSCRIBE' in l
        )
    }

def modify_labels(service, user_id='me', msg_id=None, add_labels=None, remove_labels=None):
    if msg_id is None:
        return
    
    body = {
        'addLabelIds': add_labels or [],
        'removeLabelIds': remove_labels or []
    }
    
    service.users().messages().modify(
        userId=user_id,
        id=msg_id,
        body=body
    ).execute()

def trash_message(service, user_id='me', msg_id=None):
    if msg_id is None:
        return
    
    service.users().messages().trash(
        userId=user_id,
        id=msg_id
    ).execute()

def create_label(service, user_id='me', label_name=None):
    if label_name is None:
        return None
    
    label_body = {
        'name': label_name,
        'labelListVisibility': 'labelShow',
        'messageListVisibility': 'show'
    }
    
    try:
        return service.users().labels().create(
            userId=user_id,
            body=label_body
        ).execute()
    except Exception:
        return None

def delete_labels_with_prefix(service, prefix, user_id='me'):
    """Delete all labels starting with a given prefix (e.g., 'AO/')"""
    try:
        labels = service.users().labels().list(userId=user_id).execute()
        deleted_count = 0
        for label in labels.get('labels', []):
            if label['name'].startswith(prefix):
                print(f"    Deleting label: {label['name']}")
                service.users().labels().delete(userId=user_id, id=label['id']).execute()
                deleted_count += 1
        return deleted_count
    except Exception as e:
        print(f"    Warning: Could not delete labels: {e}")
        return 0

def delete_labels_with_prefix(service, prefix, user_id='me'):
    """Delete all labels starting with a given prefix (e.g., 'AO/')"""
    try:
        labels = service.users().labels().list(userId=user_id).execute()
        deleted_count = 0
        for label in labels.get('labels', []):
            if label['name'].startswith(prefix):
                print(f"    Deleting label: {label['name']}")
                service.users().labels().delete(userId=user_id, id=label['id']).execute()
                deleted_count += 1
        return deleted_count
    except Exception as e:
        print(f"    Warning: Could not delete labels: {e}")
        return 0
