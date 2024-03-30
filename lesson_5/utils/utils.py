def parse_params(params: str):
    if params.startswith('0x'):
        params = params[2:]
    while params:
        print(params[:64])
        params = params[64:]
