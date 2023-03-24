import requests

log = "logs/12776adc-65c0-46d8-9be6-201c82606468.log"
_id = "12776adc-65c0-46d8-9be6-201c82606468"
email = "hai.srikar@gmail.com"
id_token = "eyJraWQiOiJ4M3NhZjFZTkNsRGwyVDljemdCR01ybnVVMlJlNDNjb1E1UGxYMWgwb2tBPSIsImFsZyI6IlJTMjU2In0.eyJzdWIiOiI2ODI4Y2I2My1lOGQ4LTQ4YmYtYTUzOC00NjJlZDg0N2UyNzUiLCJlbWFpbF92ZXJpZmllZCI6dHJ1ZSwiaXNzIjoiaHR0cHM6XC9cL2NvZ25pdG8taWRwLmV1LXdlc3QtMS5hbWF6b25hd3MuY29tXC9ldS13ZXN0LTFfek9mVngwcWl3IiwiY29nbml0bzp1c2VybmFtZSI6IjY4MjhjYjYzLWU4ZDgtNDhiZi1hNTM4LTQ2MmVkODQ3ZTI3NSIsIm9yaWdpbl9qdGkiOiJjNTdkZmRkMi1iNDVkLTRiOGQtYjQ1NC05OGQ3YTYwYjJlODEiLCJhdWQiOiIzMmM1ZGM1dDFrbDUxZWRjcXYzOWkwcjJzMiIsImV2ZW50X2lkIjoiM2RmOGNmMmItZTljMi00MzI2LWI2ODUtYTI2ODEzOTllNGNjIiwidG9rZW5fdXNlIjoiaWQiLCJhdXRoX3RpbWUiOjE2NzkzMzU1NjksImV4cCI6MTY3OTQyNDUyMSwiaWF0IjoxNjc5NDIwOTIxLCJqdGkiOiIzNGRmOWRkZS1jNDhjLTQzNDQtYmMzZC01OTU0YTM1NzdmMjUiLCJlbWFpbCI6ImhhaS5zcmlrYXJAZ21haWwuY29tIn0.jf6SiE7KcSr9iVeb-PgPuwiaCNGuGjCnZ6tnQ2kSSxYWeUATp9P8g-bw4vEeGHixusieIrAJIRNGEctLwISp5txzWBtXBMOilsg2MONRXJEMNsL6GbVzwsXmQ0E1PMwfrqZy3d89pOupXkIlabzGAxh2iLyldcevaw_ikYz3weF3CT4z8q0DMB8d-Yr8gJqyJE5yg26YWttttIKzmYUBhHbgul-1fH1lh7Egzy5QfjNbB2TEtFnn3AxMIf6FOK-90tdvNvM5cMa3LzsQoVlt7lXgbx2F95hEy6MvlhftxZ8YFrs0kZu57dkVtRPrUhPZECtJ-Q3-GTwFmVAcyXI9rA"
headers = {
    'Authorization': "Bearer "+id_token
}

response = requests.get(
    url=f"https://bz97lt8b1e.execute-api.eu-west-1.amazonaws.com/prod/results/tutorial/{_id}",
     headers=headers
)

if __name__ == '__main__':
    print(response.json())


# logs/d89dae17-699c-404f-9579-66ad48901ab5.log --> final value: 34.328125
#  logs/68acc095-3c1d-489c-8040-f4b23d2172c6.log --> 800 or something


# doing hyper trade by quantities of 3 -> 764 profit
# doing hyper trade by quantities of 4 -> 751 profit

# a7a11a3e -> 968 (3 quantities only on non-order matches)
# 6baf7ec5 -> 1050 (5 quantities only on non-order matches)
# 08cb8477 -> 1096 (5 quantities only on non-order matches)