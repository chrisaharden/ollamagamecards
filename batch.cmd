REM This list is good for mass generation and for mass testing, but it takes a while
REM with only one GPU.  And sometimes llama3.1 just terminates the connection. If that 
REM happens, just comment out the ones you have completed as you go, and rerun the batch file.
python ./source/main.py --config ./source/card_designs/CatTrivia.ini
python ./source/main.py --config ./source/card_designs/Cinderella.ini
python ./source/main.py --config ./source/card_designs/Deadpool.ini
python ./source/main.py --config ./source/card_designs/DogTrivia.ini
python ./source/main.py --config ./source/card_designs/FarmAnimals.ini
python ./source/main.py --config ./source/card_designs/Football.ini
python ./source/main.py --config ./source/card_designs/HarryPotterTrivia.ini
python ./source/main.py --config ./source/card_designs/MarvelTrivia.ini
python ./source/main.py --config ./source/card_designs/MaryPoppins.ini
python ./source/main.py --config ./source/card_designs/MathTrivia.ini
python ./source/main.py --config ./source/card_designs/QuestionsandAnswers.ini
python ./source/main.py --config ./source/card_designs/QuestionsOnly.ini
python ./source/main.py --config ./source/card_designs/ResponsesOnly.ini
python ./source/main.py --config ./source/card_designs/SpidermanTrivia.ini
python ./source/main.py --config ./source/card_designs/SpongeBob.ini
python ./source/main.py --config ./source/card_designs/StarWarsTrivia.ini
python ./source/main.py --config ./source/card_designs/TheFlintstonesTrivia.ini
python ./source/main.py --config ./source/card_designs/Wolverine.ini