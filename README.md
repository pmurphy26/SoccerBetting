This was orginially just some code that I had wrote that scraped data off of FotMob's API, which was then altered and fed into a neural network that I used to predict the outcomes of games in 4/5 of Europes top leagues. I later created another neural network to predict premier league and championship games with a pretty decent degree of accuracy, but I still need to move it from my google colab notebook to this project.

I created this simplictic UI and database just to hold all of the important information for my network and its predictions and make it a little easier to visualise and see certain predictions.

Unfortunately around the start of 2026 there were updates to Fotmob's API recently so this project no longer works properly for obtaining the most recent data and therefore can't make predictions for current games, but it still works for viewing old games and predictions.

## FOR RUNNING THE ACTUAL CODE

To start backend

python manage.py runserver

To start frontend

cd frontend && npm run start
