# Current Loan

Retrieve the borrower’s current active loan request.

The endpoint returns the latest loan for the authenticated borrower that is either `OPEN` or `FUNDED`.

---

## HTTPS Request

```http
GET /api/v1/loans/current_loan/
```

---

## Headers

| Name            | Type   | Description                               |
| --------------- | ------ | ----------------------------------------- |
| `Authorization` | String | `Bearer <JWT_TOKEN>` from authentication. |
| `Accept`        | String | `application/json`                        |

---

## Sample Request

### Python (Requests)

```python
import requests

url = 'http://127.0.0.1:8000/api/v1/loans/current_loan/'
headers = {
    "Authorization": "Bearer YOUR_JWT_TOKEN",
    "Accept": "application/json"
}

response = requests.get(url, headers=headers)
print(response.json())
```

---

## Sample Response

```json
[
    {
        "id": 1,
        "borrower": {
            "id": 1,
            "username": "testuser",
            "email": "",
            "role": "BORROWER",
            "balance": "0.00"
        },
        "lender": null,
        "amount": "5000.00",
        "term_months": 6,
        "interest_rate": "15.00",
        "fee": "3.75",
        "status": "OPEN",
        "created_at": "2025-09-27T20:00:15.936913Z",
        "funded_at": null,
        "total_payable": 5378.75
    }
]
```

---

## Response Parameters

| Parameter           | Type                      | Description                                       |
| ------------------- | ------------------------- | ------------------------------------------------- |
| `id`                | Integer                   | Loan request ID.                                  |
| `borrower.id`       | Integer                   | Borrower ID.                                      |
| `borrower.username` | String                    | Borrower username.                                |
| `borrower.email`    | String                    | Borrower email.                                   |
| `borrower.role`     | String                    | Borrower role (`BORROWER`).                       |
| `borrower.balance`  | String                    | Borrower wallet balance.                          |
| `lender`            | Object or null            | Lender details if funded, otherwise `null`.       |
| `amount`            | String                    | Loan amount requested.                            |
| `term_months`       | Integer                   | Loan term in months.                              |
| `interest_rate`     | String                    | Loan interest rate (%).                           |
| `fee`               | String                    | Fee applied on loan.                              |
| `status`            | String                    | Loan status (`OPEN` or `FUNDED`).                 |
| `created_at`        | String (ISO 8601)         | Loan creation datetime.                           |
| `funded_at`         | String (ISO 8601) or null | Loan funded datetime, `null` if not funded.       |
| `total_payable`     | Float                     | Total amount to repay including interest and fee. |

---

## Errors

| HTTP Code | Description                                                 |
| --------- | ----------------------------------------------------------- |
| 401       | Unauthorized – Missing or invalid JWT token.                |
| 404       | No current loan found for the borrower.                     |
| 500       | Internal Server Error – Something went wrong on the server. |
