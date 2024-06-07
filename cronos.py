import requests
import pandas as pd
from datetime import datetime
from decimal import Decimal
import time



api_url = "https://api.cronoscan.com/api"
api_key = "CADT8GAU4TJUZWA9DVGPMQX3AY58M6TXDP"


slack_api = "https://slack.com/api/chat.postMessage"
slack_token = "xoxb-6835991386448-7238516535122-qLiuFLLXvATm69CmIjhgRwlN"
slack_channel_id = "C0770FEQWSW"

slack_headers = {
    "Content-Type": "application/json",
    "Authorization": f"Bearer {slack_token}"
}

contract_addresses = {"0x431469cE9D70A5879e959bF15cFFAD003dC7f69F": 45203594826597434081312 } #tokens and the tokens' value you want
addresses = ["0x8995909dc0960fc9c75b6031d683124a4016825b","0xc9219731adfa70645be14cd5d30507266f2092c5"] #CDC addresses

list_of_tx = []

while True:

    for contract, contract_value in contract_addresses.items():
        for addr in addresses:

            params = {
                    "module" : "account",
                    "action" : "tokentx",
                    "contractaddress" : contract,
                    "address" : addr,
                    "page" : "1",
                    "offset" : "1", 
                    "sort" : "desc",
                    "apikey" : api_key
            }


            response = requests.get(api_url, params=params)

            if response.status_code == 200: 
                print(f" {datetime.now()} : Request successful")
                data = response.json()
                df = pd.DataFrame(data['result'])

                df['value'] = df['value'].apply(lambda x : Decimal(x).to_integral_value())

                if (df['value'].iloc[0] > contract_value) and (df['hash'].iloc[0] not in list_of_tx): 

                    list_of_tx.append(df['hash'].iloc[0])

                    df['timeStamp'] = pd.to_datetime(df['timeStamp'], unit='s')
                    df.drop(columns=['blockNumber','nonce','tokenSymbol','blockHash','tokenDecimal','transactionIndex','gas','gasPrice','gasUsed','cumulativeGasUsed',
                            'input','confirmations'], inplace=True)
                            
                    #post noti to slack bot
                    message = f"New transaction detected : /n {df.iloc[0]}"
                    payload = {
                        "channel": slack_channel_id,
                        "text" : message
                    }

                    try: 
                        slack_response = requests.post(slack_api,headers=slack_headers,json=payload)
                        print("Message posted successfully")
                    except:
                        print("Error sending message")


            else:
                print(f"Error: {response.status_code}")

    time.sleep(1)


