from parser import parsing, IParser


ru_parser:IParser.IParser = parsing.ParserRU()
ru_parser.start_parsing()
ru_parser.join_all_area()
