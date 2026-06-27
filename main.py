from commands.ask import ask

def main():
    response = ask("cv.pdf", "What is the main programming language of Gabriel?")
    print(response)
    
if __name__ == '__main__':
    main()


