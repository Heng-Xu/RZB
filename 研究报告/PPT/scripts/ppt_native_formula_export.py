"""Project export adapter: bind Office math namespace and apply required face.

The installed PPT Master files and its immutable native backing remain intact.
The current serializer registers transition namespaces but misses a14 when math
is introduced into an existing deck. Register that standard namespace for this
process. The project requires Times New Roman; retain compiler-produced OMML
structure and math styles while changing only its emitted typeface attributes.
"""
from pathlib import Path
import runpy,sys
K=Path('/home/xh/.codex/skills/ppt-master/scripts')
sys.path.insert(0,str(K))
import pptx_transitions
from svg_to_pptx.native_objects import formula
from svg_to_pptx.native_objects import inline_formula
pptx_transitions.TRANSITION_NAMESPACES['a14']='http://schemas.microsoft.com/office/drawing/2010/main'
original=formula._styled_omml
def project_math_face(spec):
    return original(spec).replace('typeface="Cambria Math"','typeface="Times New Roman"')
formula._styled_omml=project_math_face
original_inline=inline_formula.build_inline_formula_xml
def project_inline_math(latex,properties_xml):
    return original_inline(latex,properties_xml.replace('typeface="Cambria Math"','typeface="Times New Roman"'))
inline_formula.build_inline_formula_xml=project_inline_math
sys.argv[0]=str(K/'svg_to_pptx.py')
runpy.run_path(str(K/'svg_to_pptx.py'),run_name='__main__')
