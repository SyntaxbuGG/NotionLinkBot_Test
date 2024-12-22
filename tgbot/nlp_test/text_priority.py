from transformers import pipeline

# Используем text-classification pipeline для анализа текста
classifier = pipeline("text-classification",model='distilbert/distilbert-base-uncased-finetuned-sst-2-english')


async def analyze_priority(data_url):
    if not data_url:
        return 'Unknown'
    result = classifier(data_url)[0]  # Берём первый результат
    label = result["label"].lower()  # Достаем priority
    confidence = result["score"]  # Достаём уверенность

    if confidence < 0.3:  # Если уверенность низкая, вернем "low"
        return "low"
    if "high" in label:
        return "high"
    elif "medium" in label:
        return "medium"
    else:
        return "low"



