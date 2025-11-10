def summarize_text(llm_response):
    try:
        result = llm_response.get('result', {})
        summary_text = result.get('summary', 'No summary provided.')
        anomaly_score = result.get('anomaly_score', 0.0)
        return {'summary': summary_text, 'anomaly_score': anomaly_score}
    except Exception as e:
        return {'summary': 'Error parsing LLM output', 'anomaly_score': 0.0}
