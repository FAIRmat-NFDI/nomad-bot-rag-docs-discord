# AMETEK/Cameca CernROOT-based file formats

Please note that the proprietary file formats RRAW, STR, ROOT, RHIT, and HITS from AMETEK/Cameca are currently not processable
with software other than provided by Cameca. We have investigated the situation and were able to confirm though that a substantial number
of metadata have been documented by Cameca. In addition, we have done a successful proof-of-concept to explore a route of reading several
pieces of information contained in all of these binary file formats using Python.

The main motivation for this was to explore a route that could enable automated mapping and normalizing of some of the metadata into NeXus via a simpler - programmatic approach - than
having users to enter the information via e.g. electronic lab notebooks or supplementary files. The main motivation to access the binary file structure directly in contrast to using
a library such as from [Cern's ROOT](https://root.cern/) ecosystem is that every tool which would include a ROOT-capable pynxtools-apm plugin would also have to install at least
some part of the versatile but functionally rich ROOT library. This may not be appropriate though in all cases when working with already complex research data management systems
which have their own dependencies and thus adding ROOT would make the testing and handling of dependencies more intricate.

AMETEK/Cameca has inspected the situation and works on an implementation of features in AP Suite that will eventually allow users to
export some of these metadata via the AMETEK/Cameca APT file format that is open-source. Alternatively, also AMETEK/Cameca's custom
plugin interface is a possible avenue how metadata could be exported in the future from AMETEK/Cameca to third-party software.
When these features will be available, we are happy to work on an update of pynxtools-apm and the underlying ifes_apt_tc_data_modeling library
to support the community.
