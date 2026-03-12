import os
import yaml

MODEL_NAME = "jason23322/high-accuracy-email-classifier"

HF_TOKEN = None

USE_LIGHTWEIGHT_MODE = True

def load_hf_token():
    global HF_TOKEN
    if HF_TOKEN is None:
        try:
            with open('config.yaml', 'r') as f:
                config = yaml.safe_load(f)
                HF_TOKEN = config.get('huggingface', {}).get('token')
        except:
            pass
    return HF_TOKEN

AI_TO_TYPE = {
    '0': 'Promotions',
    '1': 'Social', 
    '2': 'Updates',
    '3': 'Personal'
}

TYPE_DISPLAY = {
    'Promotions': 'Promotions',
    'Social': 'Promotions', 
    'Updates': 'Promotions',
    'Personal': 'Personal'
}

_pipeline = None

def get_classifier():
    global _pipeline
    
    if USE_LIGHTWEIGHT_MODE:
        print("Running in LIGHTWEIGHT MODE - Using enhanced keyword-based classification")
        return None
        
    if _pipeline is None:
        print("Loading AI classifier model...")
        try:
            from transformers import pipeline
            token = load_hf_token()
            _pipeline = pipeline(
                "text-classification", 
                model=MODEL_NAME,
                token=token,
                top_k=None
            )
            print("AI classifier loaded!")
        except Exception as e:
            print(f"Could not load AI model: {e}")
            print("Using keyword-based classification instead")
            _pipeline = None
    return _pipeline

def classify_email_fallback(text_inputs):
    text = text_inputs.lower() if isinstance(text_inputs, str) else ""
    
    promotion_keywords = [
        'sale', 'discount', 'offer', 'limited time', 'buy now', 'free', 'promo', 
        'deal', 'newsletter', 'subscribe', 'update', 'digest', 'promotion', 
        'marketing', 'special offer', 'flash sale', 'weekend sale', 'clearance',
        'early access', 'exclusive deal', 'save now', 'up to %', 'off today',
        'new collection', 'shop now', 'best seller', 'trending', 'popular'
    ]
    
    social_keywords = [
        'linkedin', 'facebook', 'twitter', 'instagram', 'social network', 
        'connection request', 'profile views', 'followed you', 'liked your post',
        'commented on', 'shared your post', 'new follower', ' Connections',
        ' LinkedIn', 'meetup', 'xing', 'tiktok', 'youtube', 'snapchat'
    ]
    
    job_keywords = [
        'job', 'applied', 'application', 'interview', 'hiring', 'careers', 
        'indeed', 'career', 'job opportunity', 'job alert', 'new job', 
        'job vacancy', 'position', 'recruitment', 'resume', 'cv', 'hire',
        'job offer', 'salary', 'benefits', 'job description', 'apply now',
        'indeed prime', 'linkedin jobs', 'glassdoor', 'monster', 'ziprecruiter'
    ]
    
    receipt_keywords = [
        'receipt', 'invoice', 'order confirmed', 'order placed', 'thank you for your purchase', 
        'order summary', 'order #', 'transaction', 'thank you for ordering', 'order details',
        'order confirmation', 'purchase confirmation', 'order received', 'order status',
        'shipping confirmation', 'delivered', 'out for delivery', 'track your order',
        'order history', 'refund', 'return', 'exchange', 'canceled order'
    ]
    
    payment_keywords = [
        'payment', 'billing', 'subscription', 'charged', 'renewal', 'debit', 
        'credit card', 'payment successful', 'payment failed', 'payment due',
        'invoice #', 'bill', 'membership', 'plan', 'upgrade', 'payment method',
        'auto-renew', 'expired card', 'payment receipt', 'transaction receipt',
        'price change', 'refund processed', 'money back', 'credit processed'
    ]
    
    travel_keywords = [
        'flight', 'booking', 'hotel', 'airbnb', 'reservation', 'trip', 'travel',
        'departure', 'arrival', 'boarding pass', 'flight status', 'delayed',
        'cancellation', 'car rental', 'uber', 'lyft', 'train', 'bus ticket',
        ' itinerary', 'vacation', 'holiday', 'package', 'cruise'
    ]
    
    promo_count = sum(1 for kw in promotion_keywords if kw in text)
    social_count = sum(1 for kw in social_keywords if kw in text)
    job_count = sum(1 for kw in job_keywords if kw in text)
    receipt_count = sum(1 for kw in receipt_keywords if kw in text)
    payment_count = sum(1 for kw in payment_keywords if kw in text)
    travel_count = sum(1 for kw in travel_keywords if kw in text)
    
    if travel_count > 0:
        return 'Updates'
    elif payment_count > 0:
        return 'Payments'
    elif receipt_count > 0:
        return 'Receipts'
    elif job_count > 0:
        return 'Job'
    elif social_count > 0:
        return 'Social'
    elif promo_count > 0:
        return 'Promotions'
    else:
        return 'Personal'

def classify_email(text_inputs):
    classifier = get_classifier()
    
    if classifier is None:
        return classify_email_fallback(text_inputs)
    
    if isinstance(text_inputs, str):
        text_inputs = [text_inputs]
    
    try:
        results = classifier(text_inputs)
        
        if len(results) == 1:
            result = results[0]
            if isinstance(result, list):
                top_result = max(result, key=lambda x: x['score'])
                label = top_result['label']
            else:
                label = result['label']
        else:
            label = results[0][0]['label']
        
        mapped = AI_TO_TYPE.get(str(label), 'Promotions')
        return mapped
        
    except Exception as e:
        print(f"AI Classification error: {e}")
        return classify_email_fallback(text_inputs)

def classify_sender_ai(subjects, snippets):
    combined_text = ""
    for i, subj in enumerate(subjects[:3]):
        combined_text += f"Subject: {subj}. "
        if i < len(snippets):
            combined_text += f"Preview: {snippets[i][:100]}. "
    
    if not combined_text.strip():
        return 'Unknown'
    
    return classify_email(combined_text)
