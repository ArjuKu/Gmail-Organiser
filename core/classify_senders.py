from collections import Counter
import re

RECEIPT_KEYWORDS = ['receipt', 'invoice', 'order confirmed', 'order placed', 'thank you for your purchase', 'order summary', 'order #', 'transaction']
PAYMENT_KEYWORDS = ['payment', 'subscription', 'billing', 'charged', 'debit', 'credit card', 'payment successful', 'payment failed', 'renewal']
JOB_KEYWORDS = ['applied', 'application', 'interview', 'next steps', 'hiring', 'job opportunity', 'careers', 'job alert', 'new job', 'indeed', 'linkedin']
NEWSLETTER_KEYWORDS = ['newsletter', 'weekly', 'daily digest', 'subscribe', 'update', 'digest']
PROMOTION_KEYWORDS = ['sale', 'discount', 'offer', 'limited time', 'buy now', 'free', 'promo', 'deal']

def classify_sender(messages):
    if not messages:
        return None
    
    from_email = messages[0]['from_email']
    from_name = messages[0]['from_name']
    total = len(messages)
    
    categories = Counter(m.get('gmail_category', 'CATEGORY_UNDEFINED') for m in messages)
    most_common_category = categories.most_common(1)[0][0] if categories else 'CATEGORY_UNDEFINED'
    
    has_unsubscribe = any(m.get('has_unsubscribe', False) for m in messages)
    
    subjects = [m.get('subject', '') for m in messages]
    snippets = [m.get('snippet', '') for m in messages]
    
    sample_subjects = ' | '.join([s[:60] + '...' if len(s) > 60 else s for s in subjects[:5]])
    
    category_promotions = categories.get('CATEGORY_PROMOTIONS', 0) + categories.get('CATEGORY_PROMOTION', 0)
    category_social = categories.get('CATEGORY_SOCIAL', 0)
    category_primary = categories.get('CATEGORY_PRIMARY', 0)
    category_updates = categories.get('CATEGORY_UPDATES', 0)
    
    all_text = ' '.join(subjects + snippets).lower()
    
    receipt_score = sum(1 for kw in RECEIPT_KEYWORDS if kw in all_text)
    payment_score = sum(1 for kw in PAYMENT_KEYWORDS if kw in all_text)
    job_score = sum(1 for kw in JOB_KEYWORDS if kw in all_text)
    newsletter_score = sum(1 for kw in NEWSLETTER_KEYWORDS if kw in all_text)
    promotion_score = sum(1 for kw in PROMOTION_KEYWORDS if kw in all_text)
    
    suggested_type = 'Unknown'
    notes = []
    
    if job_score >= 1:
        suggested_type = 'Job'
        notes.append(f'Job keywords detected ({job_score} matches)')
    elif receipt_score >= 1:
        suggested_type = 'Receipts'
        notes.append(f'Receipt keywords detected ({receipt_score} matches)')
    elif payment_score >= 1:
        suggested_type = 'Payments'
        notes.append(f'Payment keywords detected ({payment_score} matches)')
    elif has_unsubscribe and (category_promotions > 0 or category_social > 0 or category_updates > 0 or promotion_score > 0):
        suggested_type = 'Promotions'
        notes.append('Has unsubscribe link, promotional category')
    elif category_promotions > 0 or promotion_score >= 2:
        suggested_type = 'Promotions'
        notes.append('Promotional category detected')
    elif category_social > 0:
        suggested_type = 'Promotions'
        notes.append('Social category detected')
    elif category_updates > 0 and has_unsubscribe:
        suggested_type = 'Promotions'
        notes.append('Updates category with unsubscribe')
    elif category_updates > 0 and newsletter_score > 0:
        suggested_type = 'Newsletters'
        notes.append('Newsletter/Updates detected')
    elif category_primary > (category_promotions + category_social + category_updates):
        suggested_type = 'Personal'
        notes.append('Primary category, likely personal')
    else:
        if has_unsubscribe:
            suggested_type = 'Promotions'
            notes.append('Has unsubscribe, defaulting to Promotions')
        else:
            notes.append(f'Category: {most_common_category}, Scores - promo:{promotion_score}, news:{newsletter_score}, job:{job_score}')
    
    return {
        'from_email': from_email,
        'example_name': from_name,
        'total_messages': total,
        'sample_subjects': sample_subjects,
        'gmail_category': most_common_category,
        'has_unsubscribe': has_unsubscribe,
        'suggested_type': suggested_type,
        'notes': '; '.join(notes) if notes else 'Analysis complete'
    }
