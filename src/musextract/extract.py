'''
Created on 29.04.2017

@author: wglas
'''

from zipfile import ZipFile
import logging
from xml.dom import pulldom
from _collections import defaultdict

log = logging.getLogger(__name__)

BAR=chr(0x1D100)
BAR_DOUBLE=chr(0x1D101)
BAR_END=chr(0x1D102)
BAR_BEGIN=chr(0x1D103)

BAR_REPEAT_END=chr(0x1D107)
BAR_REPEAT_BEGIN=chr(0x1D106)

FERMATA=chr(0x1D110)

BREATH_MARK=chr(0x1D112)

REST_MEASURE=chr(0x1D129)

RESTS= {
    
      "full":    chr(0x1D13B),
      "half":    chr(0x1D13C),
      "quarter": chr(0x1D13D),
      "eighth":  chr(0x1D13E),
      "16th":    chr(0x1D13F),
      "32th":    chr(0x1D140),
      "64th":    chr(0x1D141),
    }

def _get_text(doc,node):
    rc = []
    doc.expandNode(node)
    for node in node.childNodes:
        if node.nodeType == node.TEXT_NODE:
            rc.append(node.data)
    return ''.join(rc)

def parse_part(doc):
    
    level = 1
    
    staff_ids = []
    track_name = None
    
    for event, node in doc:
        if event == pulldom.START_ELEMENT:
            
            if level == 1 and node.tagName == "trackName":
                track_name = _get_text(doc,node)
                log.info("Got Track Name [%s]",track_name)

            elif level == 1 and node.tagName == "Staff":
                
                doc.expandNode(node)
                staff_id = node.getAttribute("id")
                log.info("Got Staff ID [%s]",staff_id)
                staff_ids.append(staff_id)
                
            else:
                if log.getEffectiveLevel() <= logging.DEBUG and level < 3:
                    log.debug("PART: %sGot <%s>."%(" "*level,node.tagName))
                level += 1
        
        elif event == pulldom.END_ELEMENT:
            
            level -= 1

            if log.getEffectiveLevel() <= logging.DEBUG and level < 3:
                log.debug("PART: %sGot </%s>."%(" "*level,node.tagName))
    
            if level == 0:
                return track_name,staff_ids

def parse_rest(doc,out):
    
    level = 1
    durationType = None
    dots = 0
    
    for event, node in doc:
        if event == pulldom.START_ELEMENT:

            if level == 1 and node.tagName == "durationType":
                durationType = _get_text(doc,node)
            elif level == 1 and node.tagName == "dots":
                dots = int(_get_text(doc,node))
            else:
                if log.getEffectiveLevel() <= logging.DEBUG and level < 3:
                    log.debug("REST: %sGot <%s>."%(" "*level,node.tagName))
                level += 1
        
        elif event == pulldom.END_ELEMENT:
            
            level -= 1

            if log.getEffectiveLevel() <= logging.DEBUG and level < 3:
                log.debug("REST: %sGot </%s>."%(" "*level,node.tagName))
    
            if level == 0:
                
                if durationType is not None:
                    
                    if durationType == "measure":
                        return 1
                    
                    out.write(RESTS[durationType])
                    
                    if dots > 0:
                        out.write("."*dots)

                return 0

def parse_lyrics(doc,out):
    
    level = 1
    syllabic = None
    text = None
    
    for event, node in doc:
        if event == pulldom.START_ELEMENT:

            if level == 1 and node.tagName == "syllabic":
                syllabic = _get_text(doc,node)
            elif level == 1 and node.tagName == "text":
                text = _get_text(doc,node)
            else:
                if log.getEffectiveLevel() <= logging.DEBUG and level < 3:
                    log.debug("REST: %sGot <%s>."%(" "*level,node.tagName))
                level += 1
        
        elif event == pulldom.END_ELEMENT:
            
            level -= 1

            if log.getEffectiveLevel() <= logging.DEBUG and level < 3:
                log.debug("REST: %sGot </%s>."%(" "*level,node.tagName))
    
            if level == 0:
                
                if text is not None:
                    
                    out.write(text)
                    
                return syllabic

def _write_rest_measures(rest_measures,out):

    if rest_measures > 0:
        out.write(REST_MEASURE)
    
    if rest_measures > 1:
        out.write(str(rest_measures))
    
    return 0

def parse_staff(doc,out):
    
    level = 1
    
    rest_measures = 0
    measure_count = 0
    last_syllabic = "unknown"
    pending_break = False
    
    for event, node in doc:
        if event == pulldom.START_ELEMENT:

            if level == 2 and node.tagName == "Rest":
                rest_measures += parse_rest(doc,out)
                pending_break = True
                
            elif level == 3 and node.tagName == "Lyrics":
                
                if pending_break:
                    print("",file=out)
                    pending_break = False
                
                if last_syllabic == "middle" or last_syllabic == "begin":
                    out.write("-")
                
                last_syllabic  = parse_lyrics(doc,out)

                if last_syllabic == "end" or last_syllabic is None:
                    out.write(" ")

            else:
                if level == 1 and node.tagName == "Measure":
    
                    rest_measures = _write_rest_measures(rest_measures,out)
    
                    if measure_count == 0:
                        out.write(BAR_BEGIN)
                    else:
                        out.write(BAR)
                    
                    measure_count +=1    
                
                if log.getEffectiveLevel() <= logging.DEBUG and level < 3:
                    log.debug("STAFF: %sGot <%s>."%(" "*level,node.tagName))
                level += 1
        
        elif event == pulldom.END_ELEMENT:
            
            level -= 1

            if log.getEffectiveLevel() <= logging.DEBUG and level < 3:
                log.debug("STAFF: %sGot </%s>."%(" "*level,node.tagName))
    
            if level == 0:
                
                _write_rest_measures(rest_measures,out)
                
                if measure_count > 0:
                    print(BAR_END,file=out)

                return

def parse_mscx(fh,voices,out):
    
    doc = pulldom.parse(fh)
    
    level = 0
    
    tracks={}
    staff_tracks = defaultdict(set)
    
    for event, node in doc:
        if event == pulldom.START_ELEMENT:
            
            if level == 2 and node.tagName=="Part":
                
                track_name,staff_ids = parse_part(doc)
                
                if track_name and staff_ids:
                    tracks[track_name] = staff_ids
                    for staff_id in staff_ids:
                        staff_tracks[staff_id].add(track_name) 
                
            elif level == 2 and node.tagName=="Staff" and staff_tracks[node.getAttribute("id")] & voices:
                
                log.info("Parsing staff with ID [%s]"%node.getAttribute("id"))
                parse_staff(doc,out)
                
            else:
                if log.getEffectiveLevel() <= logging.DEBUG and level < 3:
                    log.debug("%sGot <%s>."%(" "*level,node.tagName))
                level += 1
        
        elif event == pulldom.END_ELEMENT:
            
            level -= 1

            if log.getEffectiveLevel() <= logging.DEBUG and level < 3:
                log.debug("%sGot </%s>."%(" "*level,node.tagName))

    
    log.info("Found tracks [%s]"%(tracks,))


def parse_mscz(filename,voices,out):
    
    with ZipFile(filename,'r') as mscz_file:
        
        files = mscz_file.namelist()
        
        if log.getEffectiveLevel() <= logging.DEBUG:
            log.debug("File [%s] has entries [%s]"%(filename,files))
        
        mscx_entries = [x for x in files if x.endswith('.mscx')]
        
        if len(mscx_entries) != 1:
            raise ValueError("File [%s] has not a single .mscx entry."%filename)
        
        log.info("Parsing entry [%s] of file [%s]",mscx_entries[0],filename)
        
        with mscz_file.open(mscx_entries[0]) as mscx_file:
            parse_mscx(mscx_file,voices,out)