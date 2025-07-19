from datetime import datetime

def get_date(data_str: str, formato_str) -> datetime:
    try:
        data = datetime.strptime(data_str, formato_str)
        return data.strftime("%d/%m/%Y")
    except:
        return ""
 