"""Renders trajectory plots as PIL images for HUD overlay."""

from PIL import Image
from PIL import ImageDraw

import numpy as np





#yardsTest = np.array([0, 10, 20, 30, 40,  50, 60 ])
#inchesTest = np.array([-0.8, -5.1, -15.2, -40, -59.0, -65, -80 ])


# Cached base images (loaded once at module level)
_plotbase = Image.open("plotbase.jpg")
graph = _plotbase.copy()
rawgraph = _plotbase
draw2 = ImageDraw.Draw(graph)

_lobsterbase = Image.open("lobstermodebase2.jpg")
graph2 = _lobsterbase.copy()
rawgraph2 = _lobsterbase
draw2lo = ImageDraw.Draw(graph2)


#rawgraph = Image.open("plotbase.jpg")

def trajPlotter(distanceData: np.ndarray, dropData: np.ndarray, dist_targ: float) -> tuple:
    """Convert distance/drop arrays to plot coordinates for compact HUD mode.

    Args:
        distanceData: Range values in yards.
        dropData: Bullet path (drop) values in inches.
        dist_targ: Target distance for scaling.

    Returns:
        Tuple of (outputy, outputx) pixel coordinate arrays.
    """
    #outputy = np.zeros(len(dropData))
                
    #outputx = np.zeros((1,len(dropData[:]))
 
    outputy = elev2Y(dropData)
    outputx = range2x(distanceData,dist_targ)
     
    return outputy, outputx 
    
     
def elev2Y(inches: np.ndarray) -> np.ndarray:
    """Map elevation (inches) to Y pixel coordinates for compact plot."""
    plotHeightpx = 25 
    pxoffset  = 2 
      
    pxunits= (np.max(inches) - np.min(inches)) / plotHeightpx 
    h_max = np.max(inches) 
    
    
    youtput = np.zeros(len(inches))
    
    for i in range(len(inches)):
        youtput[i] = -(((inches[i])-h_max) / pxunits)    +  pxoffset 
        
    return youtput
    
    
def range2x(yards: np.ndarray, dist_targ: float) -> np.ndarray:
    """Map range (yards) to X pixel coordinates for compact plot."""
    plotWidthpx = 100 
    pxoffset  = 5+1 
      
    h_max = np.max(yards) 
    
    
    #if(dist_targ >= 1100 and dist_targ < 3000):
    #    divider = 1500; 
    #elif(dist_targ >= 505 and dist_targ < 1100):
    #    divider = 1000;
    #elif(dist_targ >= 255 and dist_targ < 505):
    #    divider = 500;
    #elif(dist_targ >= 0 and dist_targ < 255):
    #    divider = 250;
    
    
    
    xoutput = np.zeros(len(yards))
    
    for i in range(len(yards)):
        xoutput[i] = ((yards[i]) / dist_targ  ) * plotWidthpx    +  pxoffset  ## was /1000 or /dividier for even scaling 
        
    return xoutput  
    
    
    
    #LOB MODE PLOTTER 
def trajPlotter2(distanceData: np.ndarray, dropData: np.ndarray, dist_targ: float) -> tuple:
    """Convert distance/drop arrays to plot coordinates for lobster (full) mode."""
    #outputy = np.zeros(len(dropData))
                
    #outputx = np.zeros((1,len(dropData[:]))
 
    outputy = elev2Y2(dropData)
    outputx = range2x2(distanceData,dist_targ)
     
    return outputy, outputx 
    
    
def elev2Y2(inches: np.ndarray) -> np.ndarray:
    """Map elevation (inches) to Y pixel coordinates for lobster mode plot."""
    plotHeightpx = 180 
    pxoffset  = 2 
      
    pxunits= (np.max(inches) - np.min(inches)) / plotHeightpx 
    h_max = np.max(inches) 
    
    
    youtput = np.zeros(len(inches))
    
    for i in range(len(inches)):
        youtput[i] = -(((inches[i])-h_max) / pxunits)    +  pxoffset 
        
    return youtput
    
    
def range2x2(yards: np.ndarray, dist_targ: float) -> np.ndarray:
    """Map range (yards) to X pixel coordinates for lobster mode plot."""
    plotWidthpx = 240 
    pxoffset  = 9 
      
    h_max = np.max(yards) 
    
    
    #if(dist_targ >= 1100 and dist_targ < 3000):
    #    divider = 1500; 
    #elif(dist_targ >= 505 and dist_targ < 1100):
    #    divider = 1000;
    #elif(dist_targ >= 255 and dist_targ < 505):
    #    divider = 500;
    #elif(dist_targ >= 0 and dist_targ < 255):
    #    divider = 250;
    
    
    
    xoutput = np.zeros(len(yards))
    
    for i in range(len(yards)):
        xoutput[i] = ((yards[i]) / 3000  ) * plotWidthpx    +  pxoffset  ## was /1000 or /dividier for even scaling 
        
    return xoutput  


    
    
    


## Test the coding: 
 
def plotme(yards: np.ndarray, inches: np.ndarray, dist_targ: float, mode: int) -> Image.Image:
    """Render trajectory plot as PIL image.

    Args:
        yards: Range values in yards.
        inches: Bullet path values in inches.
        dist_targ: Target distance for scaling.
        mode: 0 = compact HUD mode, 1 = lobster (full) mode.

    Returns:
        PIL Image with trajectory overlay.
    """
    if (mode==0):
        y, x = trajPlotter(yards, inches,dist_targ)
        
        
        
        #Image.new('RGB',(150,30),(0,0,0))
        #image.show()
        
        
        
        graph.paste(rawgraph,(0,0))
       
    
    
        #print(max(x))
        #draw2.rectangle((6, 0 , 94, 180), (0,0,0))
        points = [(int(round(x[i])), int(round(y[i]))) for i in range(len(x))]
        if len(points) > 1:
            draw2.line(points, fill=(0, 120, 255), width=1)
        #graph.show() 
        return graph
        
    elif (mode==1):
    
    
        y, x = trajPlotter2(yards, inches,dist_targ)

        graph2.paste(rawgraph2,(0,0))
        
        #print(max(x))
        #draw2lo.rectangle((9, 0, 239, 177), (0,0,0))  #177
        points = [(int(round(x[i])), int(round(y[i] + 30))) for i in range(len(x))]
        if len(points) > 1:
            draw2lo.line(points, fill=(0, 120, 255), width=2)
        #graph.show() 
        

        

        
        
        
        
        
        return graph2
    
    
    
