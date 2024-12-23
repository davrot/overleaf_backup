for file in $(ls *.js)
do
	echo Copy ${file}
	docker cp ${file} sharelatex:/overleaf/services/web/modules/server-ce-scripts/scripts/
done
