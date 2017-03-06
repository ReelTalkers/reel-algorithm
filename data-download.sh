DATADIR=data/movielens/
DATASITE=http://files.grouplens.org/datasets/movielens

ZIP_FILES=("ml-1m" "ml-20m" "ml-latest" "ml-latest-small")
ZIP=".zip"
for z in "${ZIP_FILES[@]}"
do
    wget $DATASITE/$z$ZIP -P $DATADIR
    unzip -d $DATADIR $DATADIR/$z$ZIP
    rm $DATADIR/$z$ZIP
done
