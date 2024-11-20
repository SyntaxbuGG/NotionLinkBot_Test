from transformers import pipeline

# Используем text-classification pipeline для анализа текста
classifier = pipeline("text-classification")


def analyze_priority(data_url):
    result = classifier(data_url)[0]  # Берём первый результат
    label = result["label"].lower()  # Достаем priority
    confidence = result["score"]  # Достаём уверенность

    if confidence < 0.5:  # Если уверенность низкая, вернем "low"
        return "low"
    if "high" in label:
        return "high"
    elif "medium" in label:
        return "medium"
    else:
        return "low"





# priority = analyze_priority(data["content"])
# print(f"Priority: {priority}")
