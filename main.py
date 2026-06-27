from commands.report import report

def main():
    response = report("products.csv")
    print(response)
    
if __name__ == '__main__':
    main()


