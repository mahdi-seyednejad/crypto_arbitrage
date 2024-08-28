def check_insufficient_funds_error(response):
    if 'errors' in response:
        for error in response['errors']:
            # Check if the error message contains a specific substring related to fund insufficiency
            if 'enough funds' in error.get('message', '').lower():
                return True
    return False

b'{"errors":[{"id":"validation_error","message":"You don\'t have enough funds in this account for this transaction. Please try again with a smaller amount.","field":"base"}],"warnings":[{"id":"missing_version","message":"Please supply API version (YYYY-MM-DD) as CB-VERSION header","url":"https://developers.coinbase.com/api#versioning"}]}'