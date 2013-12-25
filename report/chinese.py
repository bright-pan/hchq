#coding=utf-8
#file name is chinese.py
#这个文件是在啄木鸟上抄袭的
import os
#cur_dir = os.path.dirname(os.path.abspath(__file__))
import settings
import reportlab.rl_config
reportlab.rl_config.warnOnMissingFontGlyphs = 0
import reportlab.pdfbase.pdfmetrics
import reportlab.pdfbase.ttfonts
reportlab.pdfbase.pdfmetrics.registerFont(reportlab.pdfbase.ttfonts.TTFont('yahei', u'%s%s' % (settings.CURRENT_PATH, '/static/fonts/MSYH.TTF'))) #STCAIYUN.TTF字体可以存在当前目录下
import reportlab.lib.fonts
reportlab.lib.fonts.ps2tt = lambda psfn: ('yahei', 0, 0)
reportlab.lib.fonts.tt2ps = lambda fn,b,i: 'yahei'
## for CJK Wrap
import reportlab.platypus
def wrap(self, availWidth, availHeight):
    # work out widths array for breaking
    self.width = availWidth
    leftIndent = self.style.leftIndent
    first_line_width = availWidth - (leftIndent+self.style.firstLineIndent) - self.style.rightIndent
    later_widths = availWidth - leftIndent - self.style.rightIndent
    try:
        self.blPara = self.breakLinesCJK([first_line_width, later_widths])
    except:
        self.blPara = self.breakLines([first_line_width, later_widths])
    self.height = len(self.blPara.lines) * self.style.leading
    return (self.width, self.height)

reportlab.platypus.Paragraph.wrap = wrap
