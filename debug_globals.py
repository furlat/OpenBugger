from syntax.syntax_injector import SyntaxBug
from logic.logic_injector import LogicBug
import inspect

logic_bug = LogicBug()


def fishing_script():
    # A globally accessible list
    current_labels = []
    def reset_current_labels():
        """ Clears the label list """
        global current_labels
        current_labels = []
fishing_script_str = inspect.getsource(fishing_script)
print(fishing_script_str)
fishing_script_str_mod, error, counter = logic_bug.inject(fishing_script_str,error_type="using_wrong_variable_scope",num_errors=1)

print(fishing_script_str_mod,error)