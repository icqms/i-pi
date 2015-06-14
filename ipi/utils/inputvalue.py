"""Classes used to read and write XML input and restart files.

Copyright (C) 2013, Joshua More and Michele Ceriotti

This program is free software: you can redistribute it and/or modify
it under the terms of the GNU General Public License as published by
the Free Software Foundation, either version 3 of the License, or
(at your option) any later version.

This program is distributed in the hope that it will be useful,
but WITHOUT ANY WARRANTY; without even the implied warranty of
MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the
GNU General Public License for more details.

You should have received a copy of the GNU General Public License
along with this program. If not, see <http.//www.gnu.org/licenses/>.


The classes defined in this module define the base functions which parse the
data in the restart files. Each restart object defined has a fields and an
attributes dictionary, which are filled with the tags and attributes that
are allowed to be present, along with their default values and data type.

These are then filled with the data from the xml file when the program
is initialised, and are filled by the values calculated in the program which
are then output to the checkpoint file when a restart file is required.

Also deals with checking for user input errors, of the form of misspelt tags,
bad data types, and failure to input required fields.
"""

__all__ = ['Input', 'InputValue', 'InputAttribute', 'InputArray', 'input_default']

import numpy as np
from copy import copy
from ipi.utils.io.io_xml import *
from ipi.utils.units import unit_to_internal, unit_to_user



class input_default(object):
   """Contains information required to dynamically create objects.

   Used so that we can define mutable default input values to various tags
   without the usual trouble with having a class object that is also mutable,
   namely that all members of that class share the same mutable object, so that
   changing it for one instance of that class changes it for all others. It
   does this by not holding the mutable default value, but instead the
   information to create it, so that each instance of an input class can
   have a separate instance of the default value.

   Attributes:
      type: Either a class type or function call from which to create the
         default object.
      args: A tuple giving positional arguments to be passed to the function.
      kwargs: A dictionary giving key word arguments to be passed to the
         function.
   """

   def __init__(self, factory, args = None, kwargs = None):
      """Initialises input_default.

      Args:
         type: The class or function to be used to create the default object.
         args: A tuple giving the arguments to be used to initialise
            the default value.
         kwargs: A dictionary giving the key word arguments to be used
            to initialise the default value.
      """

      if args is None:
         args = ()
      if kwargs is None:
         kwargs = {}
      # a default will be generated by factory(*args, **kwargs)
      # *args unpacks the tuple, and is used for positional arguments
      # **kwargs unpacks the dictionary, and is used for keyword arguments
      self.factory = factory
      self.args = args
      self.kwargs = kwargs


class Input(object):
   """Base class for input handling.

   Has the generic methods for dealing with the xml input file. Parses the input
   data, outputs the output data, and deals with storing and returning the
   data obtained during the simulation for the restart files.

   Attributes:
      fields: A dictionary holding the possible tags contained within the
         tags for this restart object, which are then turned into the objects
         held by the object given by this restart object. The dictionary is
         of the form:
         {"tag name": ( Input_object,
                                 {"default": default value,
                                  "dtype": data type,
                                  "options": list of available options,
                                  "help": help string,
                                  "dimension": dimensionality of data}), ... }.
      dynamic: A dictionary holding the possible tags contained within the
         tags for this restart object, which are then turned into the objects
         held by the object given by this restart object. These are used for
         tags that can be specified more than once.
         The dictionary is of the form:
         {"tag name": ( Input_object,
                                 {"default": default value,
                                  "dtype": data type,
                                  "options": list of available options,
                                  "help": help string,
                                  "dimension": dimensionality of data}), ... }.
      attribs: A dictionary holding the attribute data for the tag for this
         restart object. The dictionary is of the form:
         {"attribute name": ( Input_object,
                                 {"default": default value,
                                  "dtype": data type,
                                  "options": list of available options,
                                  "help": help string,
                                  "dimension": dimensionality of data}), ... }.
      extra: A list of tuples ( "name", Input_object ) that may be used to
         extend the capabilities of the class, i.e. to hold several instances of
         a field with the same name, or to hold variable numbers of elements.
      default_help: The default help string.
      _help: The help string of the object. Defaults to default_help.
      _default: Optional default value.
      _optional: A bool giving whether the field is a required field.
      _explicit: A bool giving whether the field has been specified by the user.
      _text: All text written between the tags of the object.
      _label: A label to be used to identify the class in the latex user manual.
      _defwrite: The string which would be output if the class has its default
         value.
   """

   fields = {}
   attribs = {}
   dynamic = {}

   default_help = "Generic input value"
   default_label = "" #used as a way to reference a particular class using
                      #hyperlinks

   def __init__(self, help=None, default=None):
      """Initialises Input.

      Automatically adds all the fields and attribs names to the input object's
      dictionary, then initialises all the appropriate input objects
      as the corresponding values.

      Args:
         help: A help string.
         default: A default value.
      """

      # list of extended (dynamic) fields
      self.extra = []

      if help is None:
         self._help = self.default_help
      else:
         self._help = help

      if isinstance(default,input_default):
         #creates default dynamically if a suitable template is defined.
         self._default = default.factory(*default.args, **default.kwargs)
      else:
         self._default = default

      self._optional = not (self._default is None)

      self._label = self.default_label

      #For each tag name in the fields and attribs dictionaries,
      #creates and object of the type given, expanding the dictionary to give
      #the arguments of the __init__() function, then adds it to the input
      #object's dictionary.
      for f, v in self.fields.iteritems():
         self.__dict__[f] = v[0](**v[1])

      for a, v in self.attribs.iteritems():
         self.__dict__[a] = v[0](**v[1])

      self.set_default()

      self._text = ""

      # stores what we would write out if the default was set
      self._defwrite = ""
      if not self._default is None:
         self._defwrite = self.write(name="%%NAME%%")

   def set_default(self):
      """Sets the default value of the object."""

      if not self._default is None:
         self.store(self._default)
      elif not hasattr(self, 'value'):
         self.value = None #Makes sure we don't get exceptions when we
                           #look for self.value

      self._explicit = False #Since the value was not set by the user

   def store(self, value=None):
      """Dummy function for storing data."""

      self._explicit = True
      pass

   def fetch(self):
      """Dummy function to retrieve data."""

      self.check()
      pass

   def check(self):
      """Base function to check for input errors.

      Raises:
         ValueError: Raised if the user does not specify a required field.
      """

      if not (self._explicit or self._optional):
         raise ValueError("Uninitialized Input value of type " + type(self).__name__)

   def extend(self, name,  xml):
      """ Dynamically add elements to the 'extra' list.

      Picks from one of the templates in the self.dynamic dictionary, then
      parses.

      Args:
         name: The tag name of the dynamically stored tag.
         xml: The xml_node object used to parse the data stored in the tags.
      """

      newfield = self.dynamic[name][0](**self.dynamic[name][1])
      newfield.parse(xml)
      self.extra.append((name,newfield))

   def write(self, name="", indent="", text="\n"):
      """Writes data in xml file format.

      Writes the tag, attributes, data and closing tag appropriate to the
      particular fields and attribs data. Writes in a recursive manner, so
      that objects contained in the fields dictionary have their write function
      called, so that their tags are written between the start and end tags
      of this object, as is required for the xml format.

      This also adds an indent to the lower levels of the xml heirarchy,
      so that it is easy to see which tags contain other tags.

      Args:
         name: An optional string giving the tag name. Defaults to "".
         indent: An optional string giving the string to be added to the start
            of the line, so usually a number of tabs. Defaults to "".
         text: Additional text to be output between the tags.

      Returns:
         A string giving all the data contained in the fields and attribs
         dictionaries, in the appropriate xml format.
      """

      rstr = indent + "<" + name;
      for a in self.attribs:
         # only write out attributes that are not defaults
         # have a very simple way to check whether they actually add something:
         # we compare with the string that would be output if the argument was set
         # to its default
         defstr = self.__dict__[a]._defwrite.replace("%%NAME%%",a)
         outstr = self.__dict__[a].write(name=a)
         if outstr != defstr:
            rstr += " " + outstr
      rstr += ">"
      rstr += text
      for f in self.fields:
         #only write out fields that are not defaults

         defstr = self.__dict__[f]._defwrite.replace("%%NAME%%",f)
         if defstr != self.__dict__[f].write(f):   # here we must compute the write string twice not to be confused by indents.
            rstr += self.__dict__[f].write(f, "   " + indent)

      for (f,v) in self.extra:
         # also write out extended (dynamic) fields if present
         rstr += v.write(f, "   " + indent)

      if text.find('\n') >= 0:
         rstr += indent + "</" + name + ">\n"
      else:
         rstr += "</" + name + ">\n"
      return rstr

   def parse(self, xml=None, text=""):
      """Parses an xml file.

      Uses the xml_node class defined in io_xml to read all the information
      contained within the root tags, and uses it to give values for the attribs
      and fields data recursively. It does this by giving all the data between
      the appropriate field tag to the appropriate field restart object as a
      string, and the appropriate attribute data to the appropriate attribs
      restart object as a string. These data are then parsed by these objects
      until all the information is read, or an input error is found.

      Args:
         xml: An xml_node object containing all the data for the parent
            tag.
         text: The data held between the start and end tags.

      Raises:
         NameError: Raised if one of the tags in the xml input file is
            incorrect.
         ValueError: Raised if the user does not specify a required field.
      """

      # before starting, sets everything to its default -- if a default is set!
      for a in self.attribs:
         self.__dict__[a].set_default()
      for f in self.fields:
         self.__dict__[f].set_default()

      self.extra = []
      self._explicit = True
      if xml is None:
         self._text = text
      else:
         for a, v in xml.attribs.iteritems():
            if a in self.attribs:
               self.__dict__[a].parse(text=v)
            elif a == "_text":
               pass
            else:
               raise NameError("Attribute name '" + a + "' is not a recognized property of '" + xml.name + "' objects")

         for (f, v) in xml.fields: #reads all field and dynamic data.
            if f in self.fields:
               self.__dict__[f].parse(xml=v)
            elif f == "_text":
               self._text = v
            elif f in self.dynamic:
               self.extend(f, v)
            else:
               raise NameError("Tag name '" + f + "' is not a recognized property of '" + xml.name + "' objects")

         #checks for missing arguments.
         for a in self.attribs:
            va = self.__dict__[a]
            if not (va._explicit or va._optional):
               raise ValueError("Attribute name '" + a + "' is mandatory and was not found in the input for the property " + xml.name)
         for f in self.fields:
            vf = self.__dict__[f]
            if not (vf._explicit or vf._optional):
               raise ValueError("Field name '" + f + "' is mandatory and was not found in the input for the property " + xml.name)

   def detail_str(self):
      """Prints out the supplementary information about a particular input class.

      Used to print out the dimensions, default value, possible options and data
      type of an input value to the LaTeX helf file.
      """

      xstr = ""
      if hasattr(self, '_dimension') and self._dimension != "undefined": #gives dimension
         xstr += "dimension: " + self._dimension + "; "

      if self._default != None and issubclass(self.__class__, InputAttribute):
         #We only print out the default if it has a well defined value.
         #For classes such as InputCell, self._default is not the value,
         #instead it is an object that is stored to give the default value in
         #self.value. For this reason we print out self.value at this stage,
         #and not self._default
         xstr += "default: " + self.pprint(self.value) + "; "

      if issubclass(self.__class__, InputAttribute):
         #if possible, prints out the type of data that is being used
         xstr += "data type: " + self.type_print(self.type) + "; "

      if hasattr(self, "_valid"):
         if self._valid is not None:
            xstr += "options: " #prints out valid options, if
            for option in self._valid:      #required.
               xstr += "`" + str(option) + "', "
            xstr = xstr.rstrip(", ")
            xstr +=  "; "
      return xstr

   def help_latex(self, name="", level=0, stop_level=None, standalone=True):
      """Function to generate a LaTeX formatted help file.

      Args:
         name: Name of the tag that has to be written out.
         level: Current level of the hierarchy being considered.
         stop_level: The depth to which information will be given. If not given,
            will give all information.
         standalone: A boolean giving whether the latex file produced will be a
            stand-alone document, or will be intended as a section of a larger
            document with cross-references between the different sections.

      Returns:
         A LaTeX formatted string.
      """

      #stops when we've printed out the prerequisite number of levels
      if (not stop_level is None and level > stop_level):
         return ""

      rstr = ""
      if level == 0:
         if standalone:
            #assumes that it is a stand-alone document, so must have
            #document options.
            rstr += r"\documentclass[12pt,fleqn]{report}"
            rstr += r"""
\usepackage{etoolbox}
\usepackage{suffix}

\newcommand{\ipiitem}[3]{%
\setul{1pt}{.4pt}\ifblank{#1}{}{\ifstrequal{#1}{\underline{\smash{}}}{}{
{\noindent\textbf{#1}:\rule{0.0pt}{1.05\baselineskip}\quad}}}% uses a strut to add a bit of vertical space
{#2}\parskip=0pt\par
\ifblank{#3}{}%
{ {\hfill\raggedleft\textit{\small #3}\par} }
}

\makeatletter
\newenvironment{ipifield}[4]{%
                \ifblank{#1}{}{\vspace{0.5em}}
               \noindent\parskip=0pt\begin{tabular}[t]{|p{1.0\linewidth}}
               %cell without border
               \multicolumn{1}{@{}p{1.0\linewidth}}{
               \ipiitem{\underline{\smash{#1}}}{#2}{}
               \ifblank{#4}{ %
                  \ifblank{#3}{}{{\hfill\raggedleft\textit{\small #3}}\par}}{} } \vspace{-1em}\\ %
               % cell with border
               \ifblank{#4}{} %
                 { \ifblank{#3}{}{\vspace{-1em}{\hfill\raggedleft\textit{\small #3}}\par} %
                 {#4}\vspace{-1em}\\\hline } % negative vspace to undo the line break
               \end{tabular}
               \parskip=0pt\list{}{\listparindent 1.5em%
                        \leftmargin    \listparindent
                        \rightmargin   0pt
                        \parsep        0pt
                        \itemsep       0pt
                        \topsep        0pt
                        }%
                \item\relax
                }
               {\endlist}
\makeatother
"""
            rstr += "\n\\begin{document}\n"
         if self._label != "" and not standalone:
            #assumes that it is part of a cross-referenced document, so only
            #starts a new section.
            rstr += "\\section{" + self._label + "}\n"
            rstr += "\\label{" + self._label + "}\n"

         rstr += "\\begin{ipifield}{}%\n"
      else:
         if self._label != "" and not standalone:
            rstr += "\\begin{ipifield}{\hyperref["+self._label+"]{"+name+"}}%\n"
         else:
            rstr += "\\begin{ipifield}{"+name+"}%\n"

      rstr += "{"+self._help+"}%\n"

      rstr += "{"+self.detail_str()+"}%\n"

      rstr += "{"
      # Prints out the attributes
      if len(self.attribs) != 0:
         #don't print out units if not necessary
         if len(self.attribs) == 1 and (("units" in self.attribs) and self._dimension == "undefined"):
            pass
         else:
            for a in self.attribs:
               #don't print out units if not necessary
               if not (a == "units" and self._dimension == "undefined"):
                  rstr += "\\ipiitem{" + a + "}%\n{" + self.__dict__[a]._help + "}%\n{"+self.__dict__[a].detail_str()+"}%\n"  #!!MUST ADD OTHER STUFF
      rstr+="}\n"

      #As above, for the fields. Only prints out if we have not reached the
      #user-specified limit.
      if len(self.fields) != 0 and level != stop_level:
         for f in self.fields:
            rstr += self.__dict__[f].help_latex(name=f, level=level+1, stop_level=stop_level, standalone=standalone)

      if len(self.dynamic) != 0 and level != stop_level:
         for f, v in self.dynamic.iteritems():
            dummy_obj = v[0](**v[1])
            rstr += dummy_obj.help_latex(name=f, level=level+1, stop_level=stop_level, standalone=standalone)

      rstr += "\\end{ipifield}\n"
      if level == 0 and standalone:
         #ends the created document if it is not part of a larger document
         rstr += "\\end{document}"

      #Some escape characters are necessary for the proper latex formatting
      rstr = rstr.replace('_', '\\_')
      rstr = rstr.replace('\\\\_', '\\_')
      rstr = rstr.replace('...', '\\ldots ')
      rstr = rstr.replace('<', '$<$')
      rstr = rstr.replace('>', '$>$')

      return rstr

   def pprint(self, default, indent="", latex = True):
      """Function to convert arrays and other objects to human-readable strings.

      Args:
         default: The object that needs to be converted to a string.
         indent: The indent at the beginning of a line.
         latex: A boolean giving whether the string will be latex-format.

      Returns:
         A formatted string.
      """

      if type(default) is np.ndarray:
         if default.shape == (0,):
            return " [ ] " #proper treatment of empty arrays.
         else:
            #indents new lines for multi-D arrays properly
            rstr = "\n" + indent + "      "
            rstr += str(default).replace("\n", "\n" + indent + "      ")
            if not latex:
               rstr += "\n" + indent + "   "

            return rstr
      elif type(default) == str:
         if latex:
            return "`" + default + "'" #indicates that it is a string
         else:
            return " " + default + " "
      elif default == []:
         return " [ ] "
      elif default == {}:
         if latex:
            return " \\{ \\} " #again, escape characters needed for latex
         else:               #formatting
            return " { } "
      else:
         #in most cases standard formatting will do
         return " " + str(default) + " "

   def type_print(self, dtype):
      """Function to convert a data types to human-readable strings.

      Args:
         dtype: A data type.
      """

      if dtype == bool:
         return "boolean"
      elif dtype == float or dtype == np.float64:
         return "float"
      elif dtype == int or dtype == np.uint64 or dtype == np.int64:
         return "integer"
      elif dtype == dict:
         return "dictionary"
      elif dtype == str:
         return "string"
      elif dtype == tuple:
         return "tuple"
      else:
         raise TypeError("Unrecognized data type " + str(dtype))

   def help_xml(self, name="", indent="", level=0, stop_level=None):
      """Function to generate an xml formatted help file.

      Args:
         name: A string giving the name of the root node.
         indent: The indent at the beginning of a line.
         level: Current level of the hierarchy being considered.
         stop_level: The depth to which information will be given. If not given,
            all information will be given

      Returns:
         An xml formatted string.
      """

      #stops when we've printed out the prerequisite number of levels
      if (not stop_level is None and level > stop_level):
         return ""

      #these are booleans which tell us whether there are any attributes
      #and fields to print out
      show_attribs = (len(self.attribs) != 0)
      show_fields = (not (len(self.fields) == 0 and len(self.dynamic) == 0)) and level != stop_level

      rstr = ""
      rstr = indent + "<" + name; #prints tag name
      for a in self.attribs:
         if not (a == "units" and self._dimension == "undefined"):
            #don't print out units if not necessary
            rstr += " " + a + "=''" #prints attribute names
      rstr += ">\n"

      #prints help string
      rstr += indent + "   <help> " + self._help + " </help>\n"
      if show_attribs:
         for a in self.attribs:
            if not (a == "units" and self._dimension == "undefined"):
               #information about tags is found in tags beginning with the name
               #of the attribute
               rstr += indent + "   <" + a + "_help> " + self.__dict__[a]._help + " </" + a + "_help>\n"

      #prints dimensionality of the object
      if hasattr(self, '_dimension') and self._dimension != "undefined":
         rstr += indent + "   <dimension> " + self._dimension + " </dimension>\n"

      if self._default != None and issubclass(self.__class__, InputAttribute):
         #We only print out the default if it has a well defined value.
         #For classes such as InputCell, self._default is not the value,
         #instead it is an object that is stored, putting the default value in
         #self.value. For this reason we print out self.value at this stage,
         #and not self._default
         rstr += indent + "   <default>" + self.pprint(self.value, indent=indent, latex=False) + "</default>\n"
      if show_attribs:
         for a in self.attribs:
            if not (a == "units" and self._dimension == "undefined"):
               if self.__dict__[a]._default is not None:
                  rstr += indent + "   <" + a + "_default>" + self.pprint(self.__dict__[a]._default, indent=indent, latex=False) + "</" + a + "_default>\n"

      #prints out valid options, if required.
      if hasattr(self, "_valid"):
         if self._valid is not None:
            rstr += indent + "   <options> " + str(self._valid) + " </options>\n"
      if show_attribs:
         for a in self.attribs:
            if not (a == "units" and self._dimension == "undefined"):
               if hasattr(self.__dict__[a], "_valid"):
                  if self.__dict__[a]._valid is not None:
                     rstr += indent + "   <" + a + "_options> " + str(self.__dict__[a]._valid) + " </" + a + "_options>\n"

      #if possible, prints out the type of data that is being used
      if issubclass(self.__class__, InputAttribute):
         rstr += indent + "   <dtype> " + self.type_print(self.type) + " </dtype>\n"
      if show_attribs:
         for a in self.attribs:
            if not (a == "units" and self._dimension == "undefined"):
               rstr += indent + "   <" + a + "_dtype> " + self.type_print(self.__dict__[a].type) + " </" + a + "_dtype>\n"

      #repeats the above instructions for any fields or dynamic tags.
      #these will only be printed if their level in the hierarchy is not above
      #the user specified limit.
      if show_fields:
         for f in self.fields:
            rstr += self.__dict__[f].help_xml(f, "   " + indent, level+1, stop_level)
         for f, v in self.dynamic.iteritems():
            #we must create the object manually, as dynamic objects are
            #not automatically added to the input object's dictionary
            dummy_obj = v[0](**v[1])
            rstr += dummy_obj.help_xml(f, "   " + indent, level+1, stop_level)

      rstr += indent + "</" + name + ">\n"
      return rstr


class InputAttribute(Input):
   """Class for handling attribute data.

   Has the methods for dealing with attribute data of the form:
   <tag_name attrib='data'> ..., where data is just a value. Takes the data and
   converts it to the required data_type, so that it can be used in the
   simulation.

   Attributes:
      type: Data type of the data.
      value: Value of data. Also specifies data type if type is None.
      _valid: An optional list of valid options.
   """

   def __init__(self,  help=None, default=None, dtype=None, options=None):
      """Initialises InputAttribute.

      Args:
         help: A help string.
         default: A default value.
         dtype: An optional data type. Defaults to None.
         options: An optional list of valid options.
      """

      if not dtype is None:
         self.type = dtype
      else:
         raise TypeError("You must provide dtype")

      super(InputAttribute,self).__init__(help, default)

      if options is not None:
         self._valid = options
         if not default is None and not self._default in self._valid:
            #This makes sure that the programmer has set the default value
            #so that it is a valid value.
            raise ValueError("Default value '" + str(self._default) + "' not in option list " + str(self._valid)+ "\n" + self._help)
      else:
         self._valid = None

   def parse(self, text=""):
      """Reads the data for a single attribute value from an xml file.

      Args:
         text: The data held between the start and end tags.
      """

      super(InputAttribute, self).parse(text=text)

      self.value = read_type(self.type, self._text)

   def store(self, value):
      """Stores the input data.

      Args:
         value: The raw data to be stored.
      """
      super(InputAttribute,self).store(value)
      self.value = value

   def fetch(self):
      """Returns the stored data."""

      super(InputAttribute,self).fetch()
      return self.value

   def check(self):
      """Function to check for input errors.

      Raises:
         ValueError: Raised if the value chosen is not one of the valid options.
      """

      super(InputAttribute,self).check()
      if not (self._valid is None or self.value in self._valid):
         #This checks that the user has set the value to a valid value.
         raise ValueError(str(self.value) + " is not a valid option (" + str(self._valid) + ")")

   def write(self, name=""):
      """Writes data in xml file format.

      Writes the attribute data in the appropriate format.

      Args:
         name: An optional string giving the attribute name. Defaults to "".

      Returns:
         A string giving the stored value in the appropriate format.
      """

      return name + "='" + write_type(self.type, self.value) + "'"


class InputValue(InputAttribute):
   """Class for handling scalar input.

   Has the methods for dealing with simple data tags of the form:
   <tag_name> data </tag_name>, where data is just a value. Takes the data and
   converts it to the required data_type, so that it can be used in the
   simulation.

   Attributes:
      units: The units that the input data is given in.
      _dimension: The dimensionality of the data.
   """

   default_dimension = "undefined"
   default_units = ""

   attribs= { "units" : ( InputAttribute, { "dtype" : str, "help" : "The units the input data is given in.", "default" : default_units } ) }

   def __init__(self,  help=None, default=None, dtype=None, options=None, dimension=None):
      """Initialises InputValue.

      Args:
         help: A help string.
         dimension: The dimensionality of the value.
         default: A default value.
         dtype: An optional data type. Defaults to None.
         options: An optional list of valid options.
      """

      # a note on units handling:
      # 1) units are only processed at parse/fetch time:
      #    internally EVERYTHING is in internal units
      # 2) if one adds an explicit "units" attribute to a derived class,
      #    the internal units handling will be just ignored
      if dimension is None:
         self._dimension = self.default_dimension
      else:
         self._dimension = dimension

      super(InputValue,self).__init__(help, default, dtype, options)

   def store(self, value, units=""):
      """Converts the data to the appropriate data type and units and stores it.

      Args:
         value: The raw data to be stored.
         units: Optional string giving the units that the data should be stored
            in.
      """

      super(InputValue,self).store(value)

      if units != "":
         self.units.store(units) #User can define in the code the units to be
                                 #printed

      self.value = value
      if self._dimension != "undefined":
         self.value *= unit_to_user(self._dimension, units, 1.0)

   def fetch(self):
      """Returns the stored data in the user defined units."""

      super(InputValue,self).fetch()

      rval = self.value
      if self._dimension != "undefined":
         rval *= unit_to_internal(self._dimension, self.units.fetch(), 1.0)
      return rval

   def write(self, name="", indent=""):
      """Writes data in xml file format.

      Writes the data in the appropriate format between appropriate tags.

      Args:
         name: An optional string giving the tag name. Defaults to "".
         indent: An optional string giving the string to be added to the start
            of the line, so usually a number of tabs. Defaults to "".

      Returns:
         A string giving the stored value in the appropriate xml format.
      """

      return Input.write(self, name=name, indent=indent, text=write_type(self.type, self.value))

   def parse(self, xml=None, text=""):
      """Reads the data for a single value from an xml file.

      Args:
         xml: An xml_node object containing the all the data for the parent
            tag.
         text: The data held between the start and end tags.
      """

      Input.parse(self, xml=xml, text=text)
      self.value = read_type(self.type, self._text)


ELPERLINE = 5
class InputArray(InputValue):
   """Class for handling array input.

   Has the methods for dealing with simple data tags of the form:
   <tag_name shape="(shape)"> data </tag_name>, where data is an array
   of the form [data[0], data[1], ... , data[length]].

   Takes the data and converts it to the required data type,
   so that it can be used in the simulation. Also holds the shape of the array,
   so that we can use a simple 1D list of data to specify a multi-dimensional
   array.

   Attributes:
      shape: The shape of the array.
   """

   attribs = copy(InputValue.attribs)
   attribs["shape"] = (InputAttribute,  {"dtype": tuple,  "help": "The shape of the array.", "default": (0,)})

   def __init__(self,  help=None, default=None, dtype=None, dimension=None):
      """Initialises InputArray.

      Args:
         help: A help string.
         dimension: The dimensionality of the value.
         default: A default value.
         dtype: An optional data type. Defaults to None.
      """

      super(InputArray,self).__init__(help, default, dtype, dimension=dimension)

   def store(self, value, units=""):
      """Converts the data to the appropriate data type, shape and units and
      stores it.

      Args:
         value: The raw data to be stored.
         units: Optional string giving the units that the data should be stored
            in.
      """

      super(InputArray,self).store(value=np.array(value, dtype=self.type).flatten().copy(), units=units)
      self.shape.store(value.shape)

      #if the shape is not specified, assume the array is linear.
      if self.shape.fetch() == (0,):
         self.shape.store((len(self.value),))

   def fetch(self):
      """Returns the stored data in the user defined units."""

      value = super(InputArray,self).fetch()

      #if the shape is not specified, assume the array is linear.
      if self.shape.fetch() == (0,):
         value = np.resize(self.value,0).copy()
      else:
         value = self.value.reshape(self.shape.fetch()).copy()

      return value

   def write(self, name="", indent=""):
      """Writes data in xml file format.

      Writes the data in the appropriate format between appropriate tags. Note
      that only ELPERLINE values are printed on each line if there are more
      than this in the array. If the values are floats, or another data type
      with a fixed width of data output, then they are aligned in columns.

      Args:
         name: An optional string giving the tag name. Defaults to "".
         indent: An optional string giving the string to be added to the start
            of the line, so usually a number of tabs. Defaults to "".

      Returns:
         A string giving the stored value in the appropriate xml format.
      """

      rstr = ""
      if (len(self.value) > ELPERLINE):
         rstr += "\n" + indent + " [ "
      else:
         rstr += " [ " #inlines the array if it is small enough

      for i, v in enumerate(self.value):
         if (len(self.value) > ELPERLINE and i > 0 and i%ELPERLINE == 0):
            rstr += "\n" + indent + "   "
         rstr += write_type(self.type, v) + ", "

      rstr = rstr.rstrip(", ") #get rid of trailing commas
      if (len(self.value) > ELPERLINE):
         rstr += " ]\n"
      else:
         rstr += " ] "

      return Input.write(self, name=name, indent=indent, text=rstr)

   def parse(self, xml=None, text=""):
      """Reads the data for an array from an xml file.

      Args:
         xml: An xml_node object containing the all the data for the parent
            tag.
         text: The data held between the start and end tags.
      """

      Input.parse(self, xml=xml, text=text)
      self.value = read_array(self.type, self._text)

      #if the shape is not specified, assume the array is linear.
      if self.shape.fetch() == (0,):
         self.shape.store((len(self.value),))
