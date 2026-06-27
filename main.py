import argparse
from commands.report import report
from commands.summarize import summarize
from commands.ask import ask


def main():
    parser = argparse.ArgumentParser(description= 'cli to increase your personal productivity while working into your projects')
    subparsers = parser.add_subparsers(dest="command")

    report_parser = subparsers.add_parser("report", help = "Generate a personal report analysis from an CSV file ")
    report_parser.add_argument("file_path", type=str, help="Type your csv file path to generate an review based of the data that you provided")

    summarize_parser = subparsers.add_parser("summarize", help = "Enter with a filepath that can be .md, .txt, .pdf, or .csv to get an LLM summary from the information you provided")
    summarize_parser.add_argument("file_path", type = str, help = "Type your file path to generate the summary")

    ask_parser = subparsers.add_parser("ask", help = "Get your questions answered regarding information derived from a file containing an LLM response." )
    ask_parser.add_argument("file_path", type = str, help = "Type the filepath of the file that you want to make questions")
    ask_parser.add_argument("ask", type = str, help = "Enter with your question to the LLM generate an answer")

    args = parser.parse_args()

    if args.command == "report":
        response = report(args.file_path)
        print(response)
    elif args.command == "summarize":
        response = summarize(args.file_path)
        print(response)
    elif args.command == "ask":
        response = ask(args.file_path, args.ask)
        print(response)
    else:
        parser.print_help()
    
    
if __name__ == '__main__':
    main()


