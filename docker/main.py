import pytesseract
from PIL import Image
from openai import OpenAI
import os
import requests
import boto3
import json
import base64

# BUDGET_ID = "00d897bf-4703-4976-af2a-35d1bdc9b673"
# YNAB_ACCESS_KEY = os.environ.get('YNAB_API_KEY')

def get_secret(secret_name: str) -> (str):
    # Create a Secrets Manager client
    client = boto3.client('secretsmanager')

    try:
        # Retrieve the secret value
        response = client.get_secret_value(SecretId=secret_name)

        # Check if the secret uses string or binary data
        if 'SecretString' in response:
            secret = response['SecretString']
            return json.loads(secret)
        else:
            return "" # if our secret is binary, that would be bad
    except Exception as e:
        print(f"Error retrieving secret: {e}")
        return ""

def decode_base64_to_file(encoded_string: str, output_file_path: str):
    """
    Decodes a base64 encoded string and writes the decoded binary data to a file.

    :param encoded_string: Base64 encoded string.
    :param output_file_path: Path to the output file.
    """
    # Decode the base64 string
    binary_data = base64.b64decode(encoded_string)

    # Write the binary data to a file
    with open(output_file_path, 'wb') as file:
        file.write(binary_data)

    print(f"File written successfully to {output_file_path}")

def process_image(file: str) -> (str, str):
    text = pytesseract.image_to_string(Image.open(file), lang='eng')

    gpt_key=get_secret("openapi-key")

    ai_client = OpenAI(
      api_key=gpt_key
    )

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


def post_transaction(budget_id: str, amnt: float, payee: str, memo: str, date: str, ynab_key: str):
    url = f'https://api.ynab.com/v1/budgets/{budget_id}/transactions'

    headers = {
        'Authorization': f'Bearer {ynab_key}',
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

    if not dry_run:
        response = requests.post(url, headers=headers, json=transaction_data)

        if response.status_code == 201:
            print('Transaction created successfully!')
        else:
            print(f'Error creating transaction. Status code: {response.status_code}')
            print(response.text)
    else:
        print("dry run, no transaction created")
        print(f"{transaction_data}")

def run_import(requeest_type: str, receipt: str, ynab_key: str, budget_id: str, dry_run: bool):
    total_cost = 0.0
    output_file_path = "/tmp/image.jpg"
    decode_base64_to_file(encoded_string, output_file_path)

    for file in ["/tmp/image.jpg"]:
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
        post_transaction(budget_id, amount, payee, memo, date)

        print()


    print("OpenAI api cost = ", total_cost)

def lambda_handler(event,context):
    print(f"Event: {event}")
    request_type=event['RequestType']
    receipt=event['Receipt']
    ynab_key=event['YnabKey']
    budget_id=event['BudgetId']
    if event['DryRun'] == "true":
        dryrun=True
    else:
        dryrun=False
    run_import(request_type, receipt, ynab_key, budget_id, dryrun)
