from handler.handler import lambda_handler

def main(event, context):
    return lambda_handler(event, context)
    
    
if __name__ == '__main__':
    main()
    


