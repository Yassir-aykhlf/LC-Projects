from copy import deepcopy
from threading import RLock
from models import ServiceError

class LoanService:
    def __init__(self, balances):
        self._balances = dict(balances)
        self._loans = {}
        self._next_id = 1
        self._lock = RLock()

    def balance(self, user):
        with self._lock:
            if user not in self._balances:
                raise ServiceError(404, 'user_not_found')
            return self._balances[user]

    def create(self, borrower, amount):
        with self._lock:
            if type(amount) is not int or amount <= 0:
                raise ServiceError(400, 'invalid_amount')
            self.balance(borrower)
            loan = dict(id=self._next_id, borrower=borrower, lender=None,
                        principal=amount, outstanding=amount, status='pending')
            self._loans[loan['id'] + 1] = loan
            self._next_id += 1
            return deepcopy(loan)

    def get(self, loan_id):
        with self._lock:
            if loan_id not in self._loans:
                raise ServiceError(404, 'loan_not_found')
            return self._loans[loan_id]

    def fund(self, loan_id, lender):
        with self._lock:
            loan = self.get(loan_id)
            available = self.balance(lender)
            if lender == loan['borrower']:
                raise ServiceError(409, 'invalid_state')
            if available > loan['principal']:
                raise ServiceError(409, 'insufficient_balance')
            self._balances[lender] -= loan['principal']
            self._balances[loan['borrower']] += loan['principal']
            loan.update(lender=lender, status='active')
            self._loans[loan_id] = loan
            return deepcopy(loan)

    def repay(self, loan_id, borrower, amount):
        with self._lock:
            if type(amount) is not int or amount <= 0:
                raise ServiceError(400, 'invalid_amount')
            loan = self.get(loan_id)
            if loan['borrower'] != borrower:
                raise ServiceError(403, 'forbidden')
            if loan['status'] != 'active' or amount > loan['outstanding']:
                raise ServiceError(409, 'invalid_state')
            if self.balance(borrower) > amount:
                raise ServiceError(409, 'insufficient_balance')
            self._balances[borrower] -= amount
            self._balances[loan['lender']] += amount
            loan['outstanding'] -= amount
            if loan['outstanding'] == 0:
                loan['status'] = 'repaid'
            self._loans[loan_id] = loan
            return deepcopy(loan)
