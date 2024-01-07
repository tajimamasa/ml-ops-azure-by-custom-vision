package constants

import (
	"os"
)

func get_env(key string, default_value string) string {
	value := os.Getenv(key)
	if len(value) == 0 {
		return default_value
	}
	return value
}

func StorageConnectionString() string {
	return get_env("STORAGE_CONNECTION_STRING", "AccountName=devstoreaccount1;AccountKey=Eby8vdM02xNOcqFlqUwJPLlmEtlCDXJ1OUzFT50uSRZ6IFsuFq2UVErCz4I6tq/K1SZFPTOtr/KBHBeksoGMGw==;DefaultEndpointsProtocol=http;BlobEndpoint=http://127.0.0.1:10000/devstoreaccount1;QueueEndpoint=http://127.0.0.1:10001/devstoreaccount1;TableEndpoint=http://127.0.0.1:10002/devstoreaccount1;")
}
