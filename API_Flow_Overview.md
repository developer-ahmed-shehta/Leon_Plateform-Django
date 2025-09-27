# Borrower
1.POST /api/v1/loan-requests/create/ → create loan request  
2.POST /api/v1/offers/<offer_id>/accept/ → accept a lender offer  
3.POST /api/v1/repayments/<repayment_id>/pay/ → pay an installment  
4.GET /api/v1/my/loans/ → view borrower’s loans  
5.GET /api/v1/loan/<loan_id>/repayments/ → view repayment schedule  
6.GET  v1/loans/<int:loan_id>/offers/ → view loan offers  

# Lender
1.GET /api/v1/loans/open/ → list all open loan requests  
2.POST /api/v1/loans/<loan_id>/offer/ → submit an offer (with interest_rate)  
3.GET /api/v1/my/offers/ → view lender’s offers  

# Debug
1.GET debug/cache/ → cache debug