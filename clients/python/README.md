# Python client for imagej-server

[`imagej_client.py`](imagej_client.py) provides a nice and clean Python API for the `imagej-server`. 

[`interactive.py`](interactive.py) demonstrates how to use the Python API with an interactive console.

## Requirements:

    - requests

Use `pip install -r requirements.txt` to install requirements.

## Usage:

(Only for the interactive console. For the Python API, refer to source code for details)

    ./imagej_client.py
    (Client) help
    
    Documented commands (type help <topic>):
    ========================================
    detail  download  help  it  iterate  list  run  stop  upload
    
    Undocumented commands:
    ======================
    EOF  exit  q  quit
    
    (Client) help list
    Lists available modules.
    
            Usage: list [-r PATTERN] [-c NUM]
    
            -r, --regex=PATTERN
                only list modules that match PATTERN
    
            -c, --count=[COUNT]
                List first COUNT modules (default: 10)
    
            Indices in the list could be used in "detail" and "run" commands.
    
    (Client) help iterate
    Iterates modules in last "list."
    
            usage:  iterate [-r] [NUM]
    
            [NUM]
                iterate the next NUM modules (default: 10)
    
            -r, --reverse
                reverse the iteration order
    
    (Client) help detail
    Shows details of a module.
    
            usage:  detail ID
    
            ID
                index of a module in the last "list", or its full name
    
    (Client) help run
    Runs a module.
    
            usage:  run (-i INPUTS | -f FILENAME) [-n] ID
    
            ID
                index of a module in the last "list", or its full name
    
            -i, --inputs=INPUTS
                inputs to the module in JSON format
    
            -f, --file=FILENAME
                file that contains the inputs in JSON format
    
            -n, --no-process
                do not do pre/post processing
    
    (Client) help upload
    Uploads a file.
    
            upload FILENAME
    
            FILENAME
                file to be uploaded
    
    (Client) help download
    Downloads a file.
    
            usage:  download [-f FORMAT] [-c CONFIG] [-d DEST] SOURCE
    
            SOURCE
                object ID obtained from "upload" or "run" if "format" is set, or
                filename obtained from "download" otherwise
    
            -f, --format=FORMAT
                file format to be saved with
    
            -c, --config=CONFIG
                configuration in JSON format for saving the file (only used if
                "format" is set)
    
            -d, --dest=DEST
                destination for saving the file (default: current directory)
    
    (Client) help stop
    Stops imagej-server gracefully.
    
            usage: stop
    
    (Client) quit

## Example

    ./imagej_client.py
    (Client) list -r PrimitiveMath
    # Module ID's that contain "PrimitiveMath"
    0: command:net.imagej.ops.math.PrimitiveMath$IntegerAbs
    1: command:net.imagej.ops.math.PrimitiveMath$IntegerAdd
    2: command:net.imagej.ops.math.PrimitiveMath$IntegerAnd
    3: command:net.imagej.ops.math.PrimitiveMath$IntegerComplement
    4: command:net.imagej.ops.math.PrimitiveMath$IntegerDivide
    5: command:net.imagej.ops.math.PrimitiveMath$IntegerLeftShift
    6: command:net.imagej.ops.math.PrimitiveMath$IntegerMax
    7: command:net.imagej.ops.math.PrimitiveMath$IntegerMin
    8: command:net.imagej.ops.math.PrimitiveMath$IntegerMultiply
    9: command:net.imagej.ops.math.PrimitiveMath$IntegerNegate
    --use "it" to show more--
    # Use "detail" to obtain parameter names for running the module
    # These calls are omitted here and after for concision
    (Client) run 1 -i '{"a": 13, "b": 22}'
    # result of "13 + 22"
    {
        "result": 35
    }
    (Client) upload ../../src/test/resources/imgs/about4.tif
    # Upload a test image and obtain its ID in imagej-server
    {
        "id": "object:8kg18dwxagwnhwu3"
    }
    (Client) list -r Create
    0: command:net.imagej.ops.create.img.CreateImgFromImg
    1: command:net.imagej.ops.create.img.CreateImgFromII
    2: command:net.imagej.ops.create.img.CreateImgFromRAI
    3: command:net.imagej.ops.create.imgFactory.CreateImgFactoryFromImg
    4: command:net.imagej.ops.create.imgLabeling.CreateImgLabelingFromInterval
    5: command:net.imagej.plugins.commands.binary.CreateMask
    6: command:net.imagej.plugins.commands.app.CreateShortcut
    7: command:net.imagej.ops.create.img.CreateImgFromDimsAndType
    8: command:net.imagej.ops.create.img.CreateImgFromInterval
    9: command:net.imagej.ops.create.imgFactory.DefaultCreateImgFactory
    --use "it" to show more--
    (Client) run 0 -i '{"in": "object:8kg18dwxagwnhwu3"}'
    # Create an image of same size to hold the output for next operation
    {
        "out": "object:y6ohl5k7lpbi0qvm"
    }
    (Client) list -r Invert
    0: command:net.imagej.ops.image.invert.InvertII
    1: command:net.imagej.plugins.commands.assign.InvertDataValues
    2: command:net.imagej.ops.math.UnaryRealTypeMath$Invert
    3: command:net.imagej.ops.transform.invertAxisView.DefaultInvertAxisView
    (Client) run 0 -i '{"in": "object:8kg18dwxagwnhwu3", "out": "object:y6ohl5k7lpbi0qvm"}'
    # Invert the test image and store it in the created image
    {
        "out": "object:y6ohl5k7lpbi0qvm"
    }
    (Client) download -f tif -d /tmp object:y6ohl5k7lpbi0qvm
    # Request the imagej-server to prepare the inverted image for download in tif format, and download it to /tmp
    {
        "filename": "al9n2mwy.tif"
    }
    (Client) quit