# TODO

## GENERIC:
    - [ ] alter SentenceData datastructure such being indexable mapping 
            of english sentence -> translation manners
    - [ ] set up jenkins pipeline, docker system tests
    - [ ] do something about repetitive entering of 'to' when adding 
          english verb meanings
    - [ ] incentivise entering of noun with article if applicable,
          entering of adjectives in consistent gender flection
    - [x] clean up options

    - write impending tests:
        - [ ] token maps
        - [ ] sentence index query
        - [ ] sentence data -> translation deduction
        - [x] forename conversion
        - [x] forename scraping
        - [x] deviation masks
    - [] abort remaining metadata related issues regarding
            forename conversion/constitution query etc.
   
## VOCABLE TRAINER:
    - [ ] refactor training loop
    - [ ] merely display related sentences possessing sufficiently low levenshtein 
      with respect to one another
    - [ ] enable english training
    - [ ] repeat faulty vocable entries within one vocable training session,
      present constant amount of entries, 
      prevent repeated successful training of same vocable entries
    - [ ] override lets go translation row on first streak occurrence
    - [ ] enable display of first vocable char on vocables user struggling with
    - [ ] tts output vocables no response was given to
    - [x] block training loop after option entrance
    - [ ] improve sentence index query
    - [ ] display rectification proposals on adding of supposedly incorrect vocables
    - [ ] enable lemma query
    - [ ] favor related sentences which haven't yet been shown
    - [ ] display incorrectly answered vocable entries after session termination and 
          number of perfected entries 
    
    - SET UP MODES:
        - [ ] vocables user struggling with
        - [ ] morphologically similar vocables (scopare, scossare, etc.)
        - [ ] random old vocables

## SENTENCE TRAINER:
    - [ ] enable input and correction of sentences if desired  

    - SET UP MODES:
        - tenses:
            - [ ] simple past
            - [ ] perfect
            - [ ] past perfect
            - [ ] simple present
            - [ ] gerund (present, past)
            - [ ] future
            - [ ] future perfect
            
        - modes:
            - [ ] imperative
            - [ ] conditional I
            - [ ] conditional II
            - [ ] subjunctive where existent
            
        - constructs:
            - [ ] negation
            - [ ] prepositions
            - [ ] conjunctions
        
__get better at writing markdowns__