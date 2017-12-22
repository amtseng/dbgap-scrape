if [ -z $1 ]
then
    echo "Usage:"
    echo "sh run_update.sh <email_address>"
    exit 0
fi

# Define some file paths
json="/cluster/u/amtseng/dbgap_scrape/data/studies_cron.json"
diff="/cluster/u/amtseng/dbgap_scrape/data/diff_cron.txt"
email="/cluster/u/amtseng/dbgap_scrape/data/email_cron.txt"

# Run scraper
python /cluster/u/amtseng/dbgap_scrape/main.py -i $json -o $json -u $diff -v

# Email contents of diff
echo "Subject: dbGaP scrape: new studies and updates" > $email
echo "To: $1" >> $email
cat $diff >> $email
sendmail $1 < $email
rm $email
