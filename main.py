import pytesseract
from PIL import Image
from openai import OpenAI
import os
import requests
import json
from datetime import date

ai_client = OpenAI()
BUDGET_ID = "00d897bf-4703-4976-af2a-35d1bdc9b673"
YNAB_ACCESS_KEY = os.environ.get('YNAB_API_KEY')


def process_image(file: str) -> dict:
    text = pytesseract.image_to_string(Image.open(file), lang='eng')

    prompt = f"""You are a receipt scanner that generates JSON.
You will recieve text extracted from a receipt, and generate JSON with 4 fields, 'grand_total', 'payee', 'memo', and 'date'.

'grand_total' is dollar amount in floating point format.
'payee' is the store the reciept is from.
'memo' is a short 3-5 word description of what was purchased
'date' is when the items were purchased in YYYY-MM-DD format. It will be within 30 days of {date.today()}
"""

    completion = ai_client.chat.completions.create(
      model="gpt-3.5-turbo-1106",
      response_format={ "type": "json_object" },
      messages=[
          {
              "role": "system", 
              "content": prompt
           },
        {"role": "user", "content": text}
      ]
    )

    msg = json.loads(completion.choices[0].message.content)
    
    cost = completion.usage.prompt_tokens *(0.0010/1000) + completion.usage.completion_tokens *(0.0020/1000)

    return msg, cost


def post_transaction(budget_id: str, amnt: float, payee: str, memo: str, date: str):
    url = f'https://api.ynab.com/v1/budgets/{budget_id}/transactions'

    headers = {
        'Authorization': f'Bearer {YNAB_ACCESS_KEY}',
        'Content-Type': 'application/json',
    }

    transaction_data = {
      "transaction": {
        "account_id": "325a756a-81b1-40c1-9bb9-3470466c9967",
        "date": f"{date}",
        "amount": amnt,
        "payee_name": f"{payee}",
        "category_id": "3fa85f64-5717-4562-b3fc-2c963f66afa6",
        "memo": f"{memo}",
        "cleared": "uncleared",
        "approved": False,
      }
    }

    response = requests.post(url, headers=headers, json=transaction_data)

    if response.status_code == 201:
        print('Transaction created successfully!')
    else:
        print(f'Error creating transaction. Status code: {response.status_code}')
        print(response.text)



def main():
    total_cost = 0.0
    for file in ["imgs/auto_store.jpg", "imgs/coffee.jpg", "imgs/gas.jpg", "imgs/liquor.jpg"]:
        gpt_dict, cost = process_image(file)
        total_cost += cost

        amount = -int(gpt_dict['grand_total'] * 1000)
        payee = gpt_dict['payee']
        memo = gpt_dict['memo']
        date = gpt_dict['date']

        print(file)
        print(gpt_dict)
        post_transaction(BUDGET_ID, amount, payee, memo, date)

        print()


    print("OpenAI api cost = ", total_cost)
    



if __name__ == '__main__':
    main()
