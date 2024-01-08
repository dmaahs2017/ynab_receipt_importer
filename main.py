import pytesseract
from PIL import Image
from openai import OpenAI
import os
import requests

ai_client = OpenAI()
BUDGET_ID = "00d897bf-4703-4976-af2a-35d1bdc9b673"
YNAB_ACCESS_KEY = os.environ.get('YNAB_API_KEY')


def process_image(file: str) -> (str, str):
    text = pytesseract.image_to_string(Image.open(file), lang='eng')

    completion = ai_client.chat.completions.create(
      model="gpt-3.5-turbo",
      messages=[
          {"role": "system", "content": "You are a receipt scanner. The user will send text extracted from a receipt, and on 4 separate lines you will print this data about the reciept. One, Grand total. Two, Payee. Three, a short 3 to 5 word memo that describe the items purchased, Four, the date of the transaction in YYYY-MM-DD format."},
        {"role": "user", "content": f"{text}"}
      ]
    )

    msg = completion.choices[0].message.content
    
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
        msg, cost = process_image(file)
        total_cost += cost

        lines = msg.split("\n")
        amount = -int(float(lines[0][14:]) * 1000)
        payee = lines[1][7:]
        memo = lines[2][6:]
        date = lines[3][6:]

        print(file)
        print("Amount: ", amount)
        print("Payee: ", payee)
        print("Memo: ", memo)
        print("Date: ", date)
        post_transaction(BUDGET_ID, amount, payee, memo, date)

        print()


    print("OpenAI api cost = ", total_cost)
    



if __name__ == '__main__':
    main()
