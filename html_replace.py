#!/usr/bin/python
from re import compile
from html.parser import HTMLParser as Parser
from sys import argv,stdin,stderr,stdout
from collections import OrderedDict 
from argparse import ArgumentParser
from html import escape
def replace_str(old,start,end,new):
    return old[:start]+new+old[end:]
class MyParser(Parser):
    def __init__(self,regex,replacement,tag='a',attr='href',*args):
        self.tag=tag
        self.attr=attr
        self.replacement=replacement
        self.regex = compile(regex)
        self.delta_length=0
        super().__init__(*args)
    def feed(self,data):
        self.data = data
        self.old_data = str(data)
        super().feed(data)
        return self.data
    def handle_starttag(self,tag,attrs):
        if tag == self.tag:
            start_pos = self.getpos()
            abs_pos = sum([len(line) for line in self.old_data.splitlines(True)][:start_pos[0]-1])+start_pos[1]+self.delta_length
            end_pos = abs_pos+len(self.get_starttag_text())
            #print(abs_pos,end_pos, self.data[abs_pos:end_pos])
            new_attrs = OrderedDict(attrs)
            if self.attr in new_attrs:
                new_attrs[self.attr]=self.regex.sub(self.replacement,new_attrs[self.attr])
            #print(new_attrs)
            new_tag = '<{} {}>'.format(self.tag,' '.join('{}="{}"'.format(attr,escape(new_attrs[attr])) for attr in new_attrs ))
            self.delta_length+= len(new_tag) - len(self.get_starttag_text())
            #print(new_tag)
            self.data = replace_str(self.data,abs_pos,end_pos,new_tag)
argparser = ArgumentParser(description="Replace links matching regex in html file")
argparser.add_argument('regex',help='Regular expression for links')
argparser.add_argument('replacement',help="Text the part of url matching regex will be replaced with. Groups matched with regex can be referenced as \\0, \\1 ,\\2 , ... , etc. Use group 0 for enitre match.")
argparser.add_argument('input_file',nargs='?',default='-',help='Name of the input file. To use standard input use "-"')
argparser.add_argument('output_file',nargs='?',default='-',help='Name of the output file. To use standard output use "-"')
args = argparser.parse_args()
parser = MyParser(args.regex,args.replacement)
if args.input_file != '-':
    f = open(args.input_file,'r',encoding='utf8')
else:
    f = stdin
if args.output_file != '-':
    g = open(args.output_file,'w',encoding='utf8')
else:
    g = stdout
print(parser.feed(f.read()),end='',file=g)
