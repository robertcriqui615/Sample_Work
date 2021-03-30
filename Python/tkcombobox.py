import tkinter as tk

from datetime import datetime
from tkinter import ttk


class SimpleComboBox(ttk.Combobox):
    """Just adds a stringvar and a get/set value for normal entries"""

    def __init__(self, master, values=None, **kwargs):

        self.values = values or []
        self._var = tk.StringVar()
        super().__init__(master, textvariable=self._var, values=self.values, **kwargs)

    @property
    def value(self):
        return self._var.get()

    @value.setter
    def value(self, val):
        self._var.set(val)

    def switchState(self):
        state = self.cget('state')

        newState = 'disabled'

        if state.string == 'disabled':
            newState = 'normal'

        self.configure(state=newState)

    def trace(self, func):
        self._var.trace('w', func)

    def addDropdownValue(self, value):
        self.values.append(value)
        self.configure(values=self.values)


class NonTypingComboBox(SimpleComboBox):

    def __init__(self, master, values=None, **kwargs):
        """
        :param master: master widget
        :param values: list of values we want for the given dropdown
        :param kwargs: any additional arguments for the Combobox
        """

        super().__init__(master, values=values, **kwargs)

        self.registerValidation()

    def registerValidation(self):
        """Registers the function we want to run when a key is entered"""

        self.configure(validate='key', validatecommand=(self.register(self.validateCommand), '%d', '%s'))

    # Make a class that will store both the lowercase and normal case of the list of values
    def validateCommand(self, action, currentValue):
        """
        All parameters are tkinter validation commands
        :param action: Insert for 1 Delete for 0
        :param currentValue: the current value of the combobox field before the change
        :param insertedValue: current text we want to enter into the combobox
        :return: True so value is validated and doesn't trigger an invalidcommand
        """
        if action == '0':
            self.value = currentValue
            return True
        else:
            return False


class ValidatedComboBox(SimpleComboBox):
    """Allows us to  validate and complete any typing the user does into a combobox"""

    def __init__(self, master, values=None, timeOut=1, **kwargs):
        """
        :param master: master widget
        :param values: list of values we want for the given dropdown
        :param timeOut: how long we want to wait to reset the search text
        :param kwargs: any additional arguments for the Combobox
        """
        self.timeOut = timeOut

        super().__init__(master, values=values, **kwargs)

        self.registerValidation()
        self.letters = []
        self.updateTime = datetime.now().timestamp()
        self.lowerCaseValues(self.values)

    def registerValidation(self):
        """Registers the function we want to run when a key is entered"""

        self.configure(validate='key', validatecommand=(self.register(self.validateCommand), '%d', '%s', '%S'))

    def toggleValidation(self, status):
        if status:
            self.configure(validate='key')
        else:
            self.configure(validate='none')

        self.value = ''

    # Make a class that will store both the lowercase and normal case of the list of values
    def validateCommand(self, action, currentValue, insertedValue):
        """
        All parameters are tkinter validation commands
        :param action: Insert for 1 Delete for 0
        :param currentValue: the current value of the combobox field before the change
        :param insertedValue: current text we want to enter into the combobox
        :return: True so value is validated and doesn't trigger an invalidcommand
        """
        if action == '0':
            self.value = ''
            return True

        newText = insertedValue.lower()
        if datetime.now().timestamp() - self.updateTime > self.timeOut:
            self.letters = [newText]
        else:
            self.letters.append(newText)

        self.updateTime = datetime.now().timestamp()

        for i, item in enumerate(self.values):
            if item.startswith(''.join(self.letters)):
                self.value = self.cget('values')[i]
                self.icursor(tk.END)
                return True

        self.value = currentValue

        return True

    def lowerCaseValues(self, values):
        """
        Sets our list of values to all lower case
        :param values: iterable of values to be stored in the combobox dropdown
        """
        self.values = [value.lower() for value in values]

    def configure(self, **kwargs):
        """
        Override the default configure if new values are passed in so that we can lowercase the values
        :param kwargs: any normal keyword arguments that would be used to configure a widget
        """

        if 'values' in kwargs:
            self.lowerCaseValues(kwargs['values'])
        super().configure(**kwargs)


class ServiceValidatedCombobox(ValidatedComboBox):
    """Just overrides the lowercasevalues function so that we can type out our service without the parcelConnect
    IE: type in prio -> and priority DDU will appear in the dropdown
    """

    def lowerCaseValues(self, values):
        self.values = [value.lower().replace('parcelconnect ', '') for value in values]
