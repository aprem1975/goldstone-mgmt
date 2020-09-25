from prompt_toolkit.document import Document
from prompt_toolkit.completion import Completion, WordCompleter, FuzzyWordCompleter
from prompt_toolkit.completion import Completer as PromptCompleter
from enum import Enum

import sys
import subprocess
import logging

stdout = logging.getLogger('stdout')

def tabular(diclst, c_name):

    rows=[]
    diclst_1=[]
    rwid=[0]*len(diclst)
    
    for i in diclst:
        d1=i.copy()
        for j in d1:
            if type(d1[j])==type([]):
                for k in range(len(d1[j])):
                    if type(d1[j][k]) != type('1'):
                        d1[j][k]=str(d1[j][k])
            elif type(d1[j])!=type('1'):
                d1[j]=str(d1[j])
        diclst_1.append(d1)

    cwid=[0]*len(c_name)

    for i in range(len(c_name)):
        if cwid[i]<len(c_name):
            cwid[i]=len(c_name[i])

    for i in range(len(diclst_1)):
        ii=0
        for j in diclst_1[i]:
            if type(diclst_1[i][j])==type([]):
                if len(diclst_1[i][j])>rwid[i]:
                    rwid[i]=len(diclst_1[i][j])
                for k in range(len(diclst_1[i][j])):
                    if cwid[ii]<len(diclst_1[i][j][k]):
                        cwid[ii]=len(diclst_1[i][j][k])
            elif cwid[ii]<len(diclst_1[i][j]):
                cwid[ii]=len(diclst_1[i][j])
            ii+=1
    print(rwid)
    cwid=[i+4 for i in cwid]

    row_bod="+"
    for i in range(len(c_name)):
        row_bod=row_bod+'-'*cwid[i]+'+'
    rows=[row_bod]

    row_bod1="+"
    for i in range(len(c_name)):
        row_bod1=row_bod1+'='*cwid[i]+'+'
    rows=[row_bod1]

    rows=[row_bod]

    row_='|'
    for i in range(len(c_name)):
        row_=row_+' '+c_name[i]+' '*(cwid[i]-len(c_name[i])-1)+'|'

    rows.append(row_)
    rows.append(row_bod1)

    for i in range(len(diclst_1)):
        row='|'
        ii=0
        for k in diclst_1[i]:
            if type(diclst_1[i][k])==type([]):
                if len(diclst_1[i][k]) == 0:
                    row=row+' '*cwid[ii]+'|'
                else:
                    row=row+' '+diclst_1[i][k][0]+' '*(cwid[ii]-len(diclst_1[i][k][0])-1)+'|'
            else:
                row=row+' '+diclst_1[i][k]+' '*(cwid[ii]-len(diclst_1[i][k])-1)+'|'
            ii+=1
        rows.append(row)
        for j in range(1,rwid[i]):
            ii=0
            row='|'
            for k in diclst_1[i]:
                if type(diclst_1[i][k])==type([]) and j<len(diclst_1[i][k]):
                    row=row+' '+diclst_1[i][k][j]+' '*(cwid[ii]-len(diclst_1[i][k][j])-1)+'|'
                else:
                    row=row+' '*cwid[ii]+'|'
                ii+=1
            rows.append(row)
        rows.append(row_bod)
    if diclst==[]:
        row='|'
        for k in range(len(c_name)):
            row = row + ' '*cwid[k]+'|'
        rows.append(row)
        rows.append(row_bod)
    return '\n'.join(rows)


class InvalidInput(Exception):
    def __init__(self, msg, candidates=[]):
        self.msg = msg
        self.candidates = candidates

    def __str__(self):
        return self.msg

class BreakLoop(Exception):
    pass

class Completer(PromptCompleter):
    def __init__(self, attrnames, valuenames=[], hook=None):
        if type(attrnames) == list:
            self._attrnames = lambda : attrnames
        else:
            self._attrnames = attrnames

        if type(valuenames) == list:
            self._valuenames = lambda _ : valuenames
        else:
            self._valuenames = valuenames

        self._hook = hook

    def get_completions(self, document, complete_event=None):
        t = document.text.split()
        if len(t) == 0 or (len(t) == 1 and document.text[-1] != ' '):
            # attribute name completion
            for c in self._attrnames():
                if c.startswith(document.text):
                    yield Completion(c, start_position=-len(document.text))
        elif len(t) > 2 or (len(t) == 2 and document.text[-1] == ' '):
            # invalid input for both get() and set(). no completion possible
            return
        else:
            # value completion

            if self._hook and self._hook():
                return

            # complete the first argument
            doc = Document(t[0])
            c = list(self.get_completions(doc))
            if len(c) == 0:
                return
            elif len(c) > 1:
                # search perfect match
                l = [v.text for v in c if v.text == t[0]]
                if len(l) == 0:
                    return
                attrname = l[0]
            else:
                attrname = c[0].text

            text = t[1] if len(t) > 1 else ''

            for c in self._valuenames(attrname):
                if c.startswith(text):
                    yield Completion(c, start_position=-len(text))


class Object(object):
    XPATH = ''
    
    class GS_Modes(Enum):
        GS_DEFAULT_MODE = 0
        GS_EXEC_MODE = 1
        GS_CONFIG_MODE = 2
        GS_INTERFACE_MODE = 3
        GS_SHOW_MODE = 4

    def __init__(self, parent, fuzzy_completion=False):
        self.parent = parent
        self._commands = {}
        self.fuzzy_completion = fuzzy_completion
        self.cli_mode = self.GS_Modes['GS_DEFAULT_MODE']
        self.privileged_user = False
         
        @self.command()
        def ping(line):
            try:
                png=' '.join(['ping'] + line)
                subprocess.call(png,shell=True)
            except KeyboardInterrupt:
                print("")
            except :
                print("Unexpected error:",sys.exc_info()[0])
        
        @self.command()
        def traceroute(line) :
            try:
                png=' '.join(['traceroute'] + line)
                subprocess.call(png,shell=True)
            except :
                print("Unexpected error:",sys.exc_info()[0])
        
        @self.command()
        def hostname(line) :
            try:
                png=' '.join(['hostname'] + line)
                subprocess.call(png,shell=True)
            except :
                print("Unexpected error:",sys.exc_info()[0])

        @self.command()
        def quit(line):
            self.close()
            if self.parent:
                return self.parent
            if (self.get_mode() is (self.GS_Modes['GS_EXEC_MODE'])):
                self.set_exec_mode(False)
                self.set_mode('GS_DEFAULT_MODE')
            raise BreakLoop()

        @self.command()
        def exit(line):
            self.close()
            return sys.exit(0)

        if self.parent:
            for k, v in self.parent._commands.items():
                if v['inherit']:
                    self._commands[k] = v
    
    def set_priv_mode(self, flag):
        self.privileged_user = flag
    
    def get_priv_mode(self):
        return (self.privileged_user)

    def set_mode(self, mode):
        self.cli_mode = self.GS_Modes[mode]
    
    def get_mode(self):
        return(self.cli_mode)

    def check_mode(self, mode):
        if (self.cli_mode is self.GS_Modes[mode]):
            return True
        else:
            return False

    def add_command(self, handler, completer=None, name=None):
        self.command(completer, name)(handler)

    def del_command(self, name):
        del self._commands[name]

    def close(self):
        pass

    def command(self, completer=None, name=None, async_=False, inherit=False, argparser=None):
        def f(func):
            self._commands[name if name else func.__name__] = {'func': func, 'completer': completer, 'async': async_, 'inherit': inherit, 'argparser': argparser}
        return f

    def help(self, text='', short=True):
        text = text.lstrip()
        try:
            v = text.split()
            if len(text) > 0 and text[-1] == ' ':
                # needs to show all candidates for the next argument
                v.append(' ')
            line = self.complete_input(v)
        except InvalidInput as e:
            return ', '.join(e.candidates)
        return line[-1].strip()

    def commands(self):
        return list(self._commands.keys())

    def completion(self, document, complete_event=None):
        # complete_event is None when this method is called by complete_input()
        if complete_event == None and len(document.text) == 0:
            return
        t = document.text.split()
        if len(t) == 0 or (len(t) == 1 and document.text[-1] != ' '):
            # command completion
            if self.fuzzy_completion and complete_event:
                c = FuzzyWordCompleter(self.commands())
                for v in c.get_completions(document, complete_event):
                    yield v
            else:
                for cmd in self.commands():
                    if cmd.startswith(document.text):
                        yield Completion(cmd, start_position=-len(document.text))
        else:
            # argument completion
            # complete command(t[0]) first
            try:
                cmd = self.complete_input([t[0]])[0]
            except InvalidInput:
                return
            v = self._commands.get(cmd)
            if not v:
                return
            c = v['completer']
            if c:
                # do argument completion with text after the command (t[0])
                new_document = Document(document.text[len(t[0]):].lstrip())
                for v in c.get_completions(new_document, complete_event):
                    yield v

    def complete_input(self, line):

        if len(line) == 0:
            raise InvalidInput('invalid command. available commands: {}'.format(self.commands()), self.commands())

        for i in range(len(line)):
            doc = Document(' '.join(line[:i+1]))
            c = list(self.completion(doc))
            if len(c) == 0:
                if i == 0:
                    raise InvalidInput('invalid command. available commands: {}'.format(self.commands()), self.commands())
                else:
                    # t[0] must be already completed
                    v = self._commands.get(line[0])
                    assert(v)
                    cmpl = v['completer']
                    if cmpl:
                        doc = Document(' '.join(line[:i] + [' ']))
                        candidates = list(v.text for v in self.completion(doc))
                        # if we don't have any candidates with empty input, it means the value needs
                        # to be passed as an opaque value
                        if len(candidates) == 0:
                            continue

                        raise InvalidInput('invalid argument. candidates: {}'.format(candidates), candidates)
                    else:
                        # no command completer, the command doesn't take any argument
                        continue
            elif len(c) > 1:
                # search for a perfect match
                t = [v for v in c if v.text == line[i]]
                if len(t) == 0:
                    candidates = [v.text for v in c]
                    raise InvalidInput('ambiguous {}. candidates: {}'.format('command' if i == 0 else 'argument', candidates), candidates)
                c[0] = t[0]
            line[i] = c[0].text
        return line 

    def _exec(self, cmd):
        line = cmd.split()
        if len(line) > 0 and len(line[0]) > 0 and line[0][0] == '!':
            line[0] = line[0][1:]
            subprocess.run(' '.join(line), shell=True)
            return None, None
        cmd = self.complete_input(line[:1])
        cmd = self._commands[cmd[0]]
        args = line[1:]
        if cmd['argparser']:
            args = cmd['argparser'].parse_args(line[1:])
        return cmd, args

    async def exec_async(self, cmd, no_fail=True):
        try:
            cmd, args = self._exec(cmd)
            if cmd == None:
                return self

            if cmd['async']:
                return await cmd['func'](args)
            else:
                return cmd['func'](args)
        except InvalidInput as e:
            if not no_fail:
                raise e
            stdout.info(str(e))
        return self

    def exec(self, cmd, no_fail=True):
        try:
            cmd, args = self._exec(cmd)
            if cmd == None:
                return self

            if cmd['async']:
                raise InvalidInput('async command not suppoted')
            return cmd['func'](args)
        except InvalidInput as e:
            if not no_fail:
                raise e
            stdout.info(str(e))
        return self
