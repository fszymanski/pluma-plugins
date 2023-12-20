# SPDX-License-Identifier: GPL-3.0-or-later
# Copyright (c) 2021-2023 Filip Szymański <fszymanski.pl@gmail.com>

import os

import gi

gi.require_version("Gtk", "3.0")
from gi.repository import Gio, Gtk

from .service import Service

PASTEBIN_SCHEMA = "org.mate.pluma.plugins.pastebin"

SYNTAX_HIGHLIGHTING = [
    ["text", "None"],
    ["4cs", "4CS"],
    ["6502acme", "6502 ACME Cross Assembler"],
    ["6502kickass", "6502 Kick Assembler"],
    ["6502tasm", "6502 TASM/64TASS"],
    ["abap", "ABAP"],
    ["actionscript", "ActionScript"],
    ["actionscript3", "ActionScript 3"],
    ["ada", "Ada"],
    ["aimms", "AIMMS"],
    ["algol68", "ALGOL 68"],
    ["apache", "Apache Log"],
    ["applescript", "AppleScript"],
    ["apt_sources", "APT Sources"],
    ["arduino", "Arduino"],
    ["arm", "ARM"],
    ["asm", "ASM (NASM)"],
    ["asp", "ASP"],
    ["asymptote", "Asymptote"],
    ["autoconf", "autoconf"],
    ["autohotkey", "Autohotkey"],
    ["autoit", "AutoIt"],
    ["avisynth", "Avisynth"],
    ["awk", "Awk"],
    ["bascomavr", "BASCOM AVR"],
    ["bash", "Bash"],
    ["basic4gl", "Basic4GL"],
    ["dos", "Batch"],
    ["bibtex", "BibTeX"],
    ["b3d", "Blitz3D"],
    ["blitzbasic", "Blitz Basic"],
    ["bmx", "BlitzMax"],
    ["bnf", "BNF"],
    ["boo", "BOO"],
    ["bf", "BrainFuck"],
    ["c", "C"],
    ["csharp", "C#"],
    ["c_winapi", "C (WinAPI)"],
    ["cpp", "C++"],
    ["cpp-winapi", "C++ (WinAPI)"],
    ["cpp-qt", "C++ (with Qt extensions"],
    ["c_loadrunner", "C: Loadrunner"],
    ["caddcl", "CAD DCL"],
    ["cadlisp", "CAD Lisp"],
    ["ceylon", "Ceylon"],
    ["cfdg", "CFDG"],
    ["c_mac", "C for Macs"],
    ["chaiscript", "ChaiScript"],
    ["chapel", "Chapel"],
    ["cil", "C Intermediate Language"],
    ["clojure", "Clojure"],
    ["klonec", "Clone C"],
    ["klonecpp", "Clone C++"],
    ["cmake", "CMake"],
    ["cobol", "COBOL"],
    ["coffeescript", "CoffeeScript"],
    ["cfm", "ColdFusion"],
    ["css", "CSS"],
    ["cuesheet", "Cuesheet"],
    ["d", "D"],
    ["dart", "Dart"],
    ["dcl", "DCL"],
    ["dcpu16", "DCPU-16"],
    ["dcs", "DCS"],
    ["delphi", "Delphi"],
    ["oxygene", "Delphi Prism (Oxygene)"],
    ["diff", "Diff"],
    ["div", "DIV"],
    ["dot", "DOT"],
    ["e", "E"],
    ["ezt", "Easytrieve"],
    ["ecmascript", "ECMAScript"],
    ["eiffel", "Eiffel"],
    ["email", "Email"],
    ["epc", "EPC"],
    ["erlang", "Erlang"],
    ["euphoria", "Euphoria"],
    ["fsharp", "F#"],
    ["falcon", "Falcon"],
    ["filemaker", "Filemaker"],
    ["fo", "FO Language"],
    ["f1", "Formula One"],
    ["fortran", "Fortran"],
    ["freebasic", "FreeBasic"],
    ["freeswitch", "FreeSWITCH"],
    ["gambas", "GAMBAS"],
    ["gml", "Game Maker"],
    ["gdb", "GDB"],
    ["gdscript", "GDScript"],
    ["genero", "Genero"],
    ["genie", "Genie"],
    ["gettext", "GetText"],
    ["go", "Go"],
    ["godot-glsl", "Godot GLSL"],
    ["groovy", "Groovy"],
    ["gwbasic", "GwBasic"],
    ["haskell", "Haskell"],
    ["haxe", "Haxe"],
    ["hicest", "HicEst"],
    ["hq9plus", "HQ9 Plus"],
    ["html4strict", "HTML"],
    ["html5", "HTML 5"],
    ["icon", "Icon"],
    ["idl", "IDL"],
    ["ini", "INI file"],
    ["inno", "Inno Script"],
    ["intercal", "INTERCAL"],
    ["io", "IO"],
    ["ispfpanel", "ISPF Panel Definition"],
    ["j", "J"],
    ["java", "Java"],
    ["java5", "Java 5"],
    ["javascript", "JavaScript"],
    ["jcl", "JCL"],
    ["jquery", "jQuery"],
    ["json", "JSON"],
    ["julia", "Julia"],
    ["kixtart", "KiXtart"],
    ["kotlin", "Kotlin"],
    ["ksp", "KSP (Kontakt Script)"],
    ["latex", "Latex"],
    ["ldif", "LDIF"],
    ["lb", "Liberty BASIC"],
    ["lsl2", "Linden Scripting"],
    ["lisp", "Lisp"],
    ["llvm", "LLVM"],
    ["locobasic", "Loco Basic"],
    ["logtalk", "Logtalk"],
    ["lolcode", "LOL Code"],
    ["lotusformulas", "Lotus Formulas"],
    ["lotusscript", "Lotus Script"],
    ["lscript", "LScript"],
    ["lua", "Lua"],
    ["m68k", "M68000 Assembler"],
    ["magiksf", "MagikSF"],
    ["make", "Make"],
    ["mapbasic", "MapBasic"],
    ["markdown", "Markdown"],
    ["matlab", "MatLab"],
    ["mercury", "Mercury"],
    ["metapost", "MetaPost"],
    ["mirc", "mIRC"],
    ["mmix", "MIX Assembler"],
    ["mk-61", "MK-61/52"],
    ["modula2", "Modula 2"],
    ["modula3", "Modula 3"],
    ["68000devpac", "Motorola 68000 HiSoft Dev"],
    ["mpasm", "MPASM"],
    ["mxml", "MXML"],
    ["mysql", "MySQL"],
    ["nagios", "Nagios"],
    ["netrexx", "NetRexx"],
    ["newlisp", "newLISP"],
    ["nginx", "Nginx"],
    ["nim", "Nim"],
    ["nsis", "NullSoft Installer"],
    ["oberon2", "Oberon 2"],
    ["objeck", "Objeck Programming Langua"],
    ["objc", "Objective C"],
    ["ocaml", "OCaml"],
    ["ocaml-brief", "OCaml Brief"],
    ["octave", "Octave"],
    ["pf", "OpenBSD PACKET FILTER"],
    ["glsl", "OpenGL Shading"],
    ["oorexx", "Open Object Rexx"],
    ["oobas", "Openoffice BASIC"],
    ["oracle8", "Oracle 8"],
    ["oracle11", "Oracle 11"],
    ["oz", "Oz"],
    ["parasail", "ParaSail"],
    ["parigp", "PARI/GP"],
    ["pascal", "Pascal"],
    ["pawn", "Pawn"],
    ["pcre", "PCRE"],
    ["per", "Per"],
    ["perl", "Perl"],
    ["perl6", "Perl 6"],
    ["phix", "Phix"],
    ["php", "PHP"],
    ["php-brief", "PHP Brief"],
    ["pic16", "Pic 16"],
    ["pike", "Pike"],
    ["pixelbender", "Pixel Bender"],
    ["pli", "PL/I"],
    ["plsql", "PL/SQL"],
    ["postgresql", "PostgreSQL"],
    ["postscript", "PostScript"],
    ["povray", "POV-Ray"],
    ["powerbuilder", "PowerBuilder"],
    ["powershell", "PowerShell"],
    ["proftpd", "ProFTPd"],
    ["progress", "Progress"],
    ["prolog", "Prolog"],
    ["properties", "Properties"],
    ["providex", "ProvideX"],
    ["puppet", "Puppet"],
    ["purebasic", "PureBasic"],
    ["pycon", "PyCon"],
    ["python", "Python"],
    ["pys60", "Python for S60"],
    ["q", "q/kdb+"],
    ["qbasic", "QBasic"],
    ["qml", "QML"],
    ["rsplus", "R"],
    ["racket", "Racket"],
    ["rails", "Rails"],
    ["rbs", "RBScript"],
    ["rebol", "REBOL"],
    ["reg", "REG"],
    ["rexx", "Rexx"],
    ["robots", "Robots"],
    ["roff", "Roff Manpage"],
    ["rpmspec", "RPM Spec"],
    ["ruby", "Ruby"],
    ["gnuplot", "Ruby Gnuplot"],
    ["rust", "Rust"],
    ["sas", "SAS"],
    ["scala", "Scala"],
    ["scheme", "Scheme"],
    ["scilab", "Scilab"],
    ["scl", "SCL"],
    ["sdlbasic", "SdlBasic"],
    ["smalltalk", "Smalltalk"],
    ["smarty", "Smarty"],
    ["spark", "SPARK"],
    ["sparql", "SPARQL"],
    ["sqf", "SQF"],
    ["sql", "SQL"],
    ["sshconfig", "SSH Config"],
    ["standardml", "StandardML"],
    ["stonescript", "StoneScript"],
    ["sclang", "SuperCollider"],
    ["swift", "Swift"],
    ["systemverilog", "SystemVerilog"],
    ["tsql", "T-SQL"],
    ["tcl", "TCL"],
    ["teraterm", "Tera Term"],
    ["texgraph", "TeXgraph"],
    ["thinbasic", "thinBasic"],
    ["typescript", "TypeScript"],
    ["typoscript", "TypoScript"],
    ["unicon", "Unicon"],
    ["uscript", "UnrealScript"],
    ["upc", "UPC"],
    ["urbi", "Urbi"],
    ["vala", "Vala"],
    ["vbnet", "VB.NET"],
    ["vbscript", "VBScript"],
    ["vedit", "Vedit"],
    ["verilog", "VeriLog"],
    ["vhdl", "VHDL"],
    ["vim", "VIM"],
    ["vb", "VisualBasic"],
    ["visualfoxpro", "VisualFoxPro"],
    ["visualprolog", "Visual Pro Log"],
    ["whitespace", "WhiteSpace"],
    ["whois", "WHOIS"],
    ["winbatch", "Winbatch"],
    ["xbasic", "XBasic"],
    ["xml", "XML"],
    ["xojo", "Xojo"],
    ["xorg_conf", "Xorg Config"],
    ["xpp", "XPP"],
    ["yaml", "YAML"],
    ["yara", "YARA"],
    ["z80", "Z80 Assembler"],
    ["zxbasic", "ZXBasic"]
]


@Gtk.Template(filename=os.path.join(os.path.dirname(os.path.abspath(__file__)), "pastebindialog.ui"))
class PastebinDialog(Gtk.Dialog):
    __gtype_name__ = "PastebinDialog"

    stack = Gtk.Template.Child()
    name_entry = Gtk.Template.Child()
    format_combo = Gtk.Template.Child()
    expiry_combo = Gtk.Template.Child()
    private_check = Gtk.Template.Child()
    spinner = Gtk.Template.Child()
    vbox = Gtk.Template.Child()
    cancel_button = Gtk.Template.Child()
    upload_button = Gtk.Template.Child()

    def __init__(self, window):
        super().__init__()

        self.doc = window.get_active_document()

        self.set_transient_for(window)

        for hl in SYNTAX_HIGHLIGHTING:
            self.format_combo.append(*hl)

        for date in [["N", "Never"],
                     ["10M", "Ten minutes"],
                     ["1H", "One hour"],
                     ["1D", "One day"],
                     ["1W", "One week"],
                     ["2W", "Two weeks"],
                     ["1M", "One month"],
                     ["6M", "Six months"],
                     ["1Y", "One year"]]:
            self.expiry_combo.append(*date)

        self.read_settings()

        self.connect("destroy", lambda _: self.write_settings())

    @Gtk.Template.Callback()
    def cancel_button_clicked(self, *_):
        self.destroy()

    @Gtk.Template.Callback()
    def upload_button_clicked(self, *_):
        self.stack.set_visible_child(self.spinner)

        self.cancel_button.set_label("Close")
        self.upload_button.set_sensitive(False)

        try:
            link = Service.upload(self.get_active_document_text(),
                                  self.name_entry.get_text(),
                                  self.format_combo.get_active_id(),
                                  "1" if self.private_check.get_active() else "0",
                                  self.expiry_combo.get_active_id())
        except Exception as err:
            err_label = Gtk.Label.new(str(err))
            self.vbox.add(err_label)
        else:
            link_button = Gtk.LinkButton.new(link)
            self.vbox.add(link_button)

        self.vbox.show_all()

        self.stack.set_visible_child(self.vbox)

    def get_active_document_text(self):
        if self.doc.get_has_selection():
            start, end = self.doc.get_selection_bounds()
        else:
            start = self.doc.get_start_iter()
            end = self.doc.get_end_iter()

        return self.doc.get_text(start, end, False)

    def read_settings(self):
        self.name_entry.set_text(self.doc.get_short_name_for_display())

        settings = Gio.Settings.new(PASTEBIN_SCHEMA)
        self.format_combo.set_active_id(settings.get_string("paste-format"))
        self.expiry_combo.set_active_id(settings.get_string("paste-expire-date"))
        self.private_check.set_active(settings.get_boolean("paste-private"))

    def write_settings(self):
        settings = Gio.Settings.new(PASTEBIN_SCHEMA)
        settings.set_string("paste-format", self.format_combo.get_active_id())
        settings.set_string("paste-expire-date", self.expiry_combo.get_active_id())
        settings.set_boolean("paste-private", self.private_check.get_active())
