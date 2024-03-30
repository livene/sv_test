def parse_params(params):
    params = params[2:]
    while params:
        print(params[:64])
        params = params[64:]
