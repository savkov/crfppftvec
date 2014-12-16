##What is this?

The crfppftvec module converts a simple feature vector notation to a 
[CRF++](http://crfpp.googlecode.com/svn/trunk/doc/index.html) template file.
This could be useful in case you want to dynamically configure and train a 
classifier using CRF++.

Simple notation:

    word[0:3];pos[-2:3];bipos[-2:2];triword[-3:2];B

...where word[x,y] stands for token features from x to y, bipos[x,y] stands for
bigram POS tag features between x and y, and triword[x,y] stands for trigram 
features between x and y. 
See [here](http://crfpp.googlecode.com/svn/trunk/doc/index.html#templ) for more 
details on CRF++ feature templates.

Resulting CRF++ template:

    U00:%x[0,0]
    U01:%x[1,0]
    U02:%x[2,0]
    U03:%x[3,0]
    U04:%x[-2,1]
    U05:%x[-1,1]
    U06:%x[0,1]
    U07:%x[1,1]
    U08:%x[2,1]
    U09:%x[3,1]
    U10:%x[-2,1]/%x[-1,1]
    U11:%x[-1,1]/%x[0,1]
    U12:%x[0,1]/%x[1,1]
    U13:%x[1,1]/%x[2,1]
    U14:%x[-3,0]/%x[-2,0]/%x[-1,0]
    U15:%x[-2,0]/%x[-1,0]/%x[0,0]
    U16:%x[-1,0]/%x[0,0]/%x[1,0]
    U17:%x[0,0]/%x[1,0]/%x[2,0]
    B

##Usage

Use `to_crfpp_template` to convert simple notation to CRF++ template.

    from crfppftvec import to_crfpp_template
    ftvec = 'word[0:3];pos[-2:3];bipos[-2:2];triword[-3:2];B'
    template = to_crfpp_template(ftvec)
    
    