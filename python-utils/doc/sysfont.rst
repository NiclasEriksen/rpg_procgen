.. module:: sysfont
   :synopsis: Font dectection helpers

sysfont - Font detection helpers
================================
The :mod:`sysfont` module enables you to find fonts installed on the
underlying operating system. It supports Win32 and fontconfig-based
(most Unix-like ones, such as Linux or BSD) systems.

.. data:: STYLE_NORMAL

   Indicates a normal font style.

.. data:: STYLE_BOLD

   Indicates a bold font style.

.. data:: STYLE_ITALIC

   Indicates an italic font style.

.. function:: init() -> None

   Initializes the internal font cache. This does not need to be called
   explicitly. It is called automatically, if one of the retrieval functions
   is executed for the first time.

.. function:: get_font(name : string[, style=STYLE_NORMAL[, ftype=None]]) -> (str, str, int, str, str)

   Retrieves the best matching font file for the given *name* and criteria.
   The return value will be a, containing the following information:
   *(family, font name, font style, font type, filename)*

   * family: string, denotes the font family
   * font name: string, the name of the font
   * font style: int, a combination of the different ``STYLE_`` values
   * font type: string, the font file type (e.g. TTF, OTF, ...)
   * filename: the name of the physical file
   
   If no font could be found, ``None`` will be returned.
   
.. function:: get_fonts(name : string[, style=STYLE_NORMAL[, ftype=None]]) -> ((str, str, int, str, str), ...)

   Retrieves all fonts matching the given family or font name, *style* and, if
   provided, font file type. The return values will be tuples, containing the
   following information: *(family, font name, font style, font type, filename)*

   * family: string, denotes the font family
   * font name: string, the name of the font
   * font style: int, a combination of the different ``STYLE_`` values
   * font type: string, the font file type (e.g. TTF, OTF, ...)
   * filename: the name of the physical file
   
   If no font could be found, ``None`` will be returned.
   
.. function:: list_fonts() -> iterator

   Retrieves an iterator over all found fonts. The values of the
   iterator will be tuples, containing the following information:
   *(family, font name, font style, font type, filename)*

   * family: string, denotes the font family
   * font name: string, the name of the font
   * font style: int, a combination of the different ``STYLE_`` values
   * font type: string, the font file type (e.g. TTF, OTF, ...)
   * filename: the name of the physical file


