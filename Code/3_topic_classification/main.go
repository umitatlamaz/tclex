package main

import (
	"bufio"
	"bytes"
	"encoding/csv"
	"encoding/json"
	"fmt"
	"io"
	"log"
	"net/http"
	"os"
	"strconv"
	"strings"
	"sync"
)

const (
	geminiAPI  = "https://generativelanguage.googleapis.com/v1beta/models/gemini-2.5-flash:generateContent"
	apiKey     = ""
	inputFile  = "lemma_pos_for_classification_may_16.csv"
	labelsFile = "kavram_listesi.txt"
	outputFile = "classified_lemma_pos_yt.csv"
	maxWorkers = 4
)

type GeminiRequest struct {
	Contents []struct {
		Parts []struct {
			Text string `json:"text"`
		} `json:"parts"`
	} `json:"contents"`
}

type GeminiResponse struct {
	Candidates []struct {
		Content struct {
			Parts []struct {
				Text string `json:"text"`
			} `json:"parts"`
		} `json:"content"`
	} `json:"candidates"`
}

type ClassificationJob struct {
	index          int
	lemma          string
	pos            string
	classification string
	err            error
}

func getLabels() ([]string, error) {
	f, err := os.Open(labelsFile)
	if err != nil {
		return nil, err
	}
	defer f.Close()

	scanner := bufio.NewScanner(f)
	var labels []string
	for scanner.Scan() {
		label := strings.TrimSpace(scanner.Text())
		if label != "" {
			labels = append(labels, label)
		}
	}
	if err := scanner.Err(); err != nil {
		return nil, err
	}
	return labels, nil
}

func readInputCSV(filepath string) ([]ClassificationJob, error) {
	f, err := os.Open(filepath)
	if err != nil {
		return nil, err
	}
	defer f.Close()

	reader := csv.NewReader(f)
	records, err := reader.ReadAll()
	if err != nil {
		return nil, err
	}

	var jobs []ClassificationJob
	for i := 1; i < len(records); i++ {
		if len(records[i]) >= 2 {
			lemma := strings.TrimSpace(records[i][0])
			pos := strings.TrimSpace(records[i][1])
			if lemma != "" {
				jobs = append(jobs, ClassificationJob{
					index: i - 1,
					lemma: lemma,
					pos:   pos,
				})
			}
		}
	}
	return jobs, nil
}

func isValidLabel(classification string, validLabels []string) bool {
	classification = strings.TrimSpace(classification)
	for _, label := range validLabels {
		if strings.EqualFold(classification, label) {
			return true
		}
	}
	return false
}

func classifyMWE(lemma string, pos string, labels []string) (string, error) {
	labelsText := ""
	for _, label := range labels {
		labelsText += label + ", "
	}

	prompt := fmt.Sprintf("Sen Türkçe ifade sınıflandırma uzmanısın. Sana verilen ifadeleri tek bir kategori ile sınıflandırıyorsun. Yorum yapmıyorsun. Bu bilgilere göre '%s' (Kelime Türü: %s) ifadesi aşağıdaki sınıflandırmalardan hangisine ait? %s", lemma, pos, labelsText)

	reqBody := GeminiRequest{}
	reqBody.Contents = make([]struct {
		Parts []struct {
			Text string `json:"text"`
		} `json:"parts"`
	}, 1)
	reqBody.Contents[0].Parts = make([]struct {
		Text string `json:"text"`
	}, 1)
	reqBody.Contents[0].Parts[0].Text = prompt

	jsonData, err := json.Marshal(reqBody)
	if err != nil {
		return "", err
	}

	req, err := http.NewRequest("POST", geminiAPI+"?key="+apiKey, bytes.NewBuffer(jsonData))
	if err != nil {
		return "", err
	}

	req.Header.Set("Content-Type", "application/json")

	client := &http.Client{}
	resp, err := client.Do(req)
	if err != nil {
		return "", err
	}
	defer resp.Body.Close()

	body, err := io.ReadAll(resp.Body)
	if err != nil {
		return "", err
	}

	var geminiResp GeminiResponse
	err = json.Unmarshal(body, &geminiResp)
	if err != nil {
		return "", err
	}

	if len(geminiResp.Candidates) > 0 && len(geminiResp.Candidates[0].Content.Parts) > 0 {
		return geminiResp.Candidates[0].Content.Parts[0].Text, nil
	}

	return "", fmt.Errorf("no response from Gemini API")
}

func worker(jobs <-chan ClassificationJob, results chan<- ClassificationJob, labels []string, wg *sync.WaitGroup) {
	defer wg.Done()
	for job := range jobs {
		classification, err := classifyMWE(job.lemma, job.pos, labels)
		job.classification = classification
		job.err = err
		results <- job
	}
}

func validateAndFixClassifications(filepath string, validLabels []string) error {
	csvFile, err := os.Open(filepath)
	if err != nil {
		return err
	}
	defer csvFile.Close()

	reader := csv.NewReader(csvFile)
	var records [][]string
	records, err = reader.ReadAll()
	if err != nil {
		return err
	}

	for i := 1; i < len(records); i++ {
		if len(records[i]) > 2 {
			if !isValidLabel(records[i][2], validLabels) {
				fmt.Printf("Halüsinasyon tespit edildi: '%s' (%s) -> '%s'\n", records[i][0], records[i][1], records[i][2])
				records[i][2] = "Halüsinasyon"
			}
		}
	}

	outFile, err := os.Create(filepath)
	if err != nil {
		return err
	}
	defer outFile.Close()

	writer := csv.NewWriter(outFile)
	defer writer.Flush()

	return writer.WriteAll(records)
}

func getUserInput() int {
	reader := bufio.NewReader(os.Stdin)
	fmt.Print("Kaç satır lemmayı sınıflandırmak istiyorsunuz? (0 = tüm veri): ")
	input, _ := reader.ReadString('\n')
	input = strings.TrimSpace(input)

	limit, err := strconv.Atoi(input)
	if err != nil || limit < 0 {
		fmt.Println("Geçersiz giriş. Tüm veri sınıflandırılacak.")
		return 0
	}
	return limit
}

func main() {
	labels, err := getLabels()
	if err != nil {
		log.Fatalf("Error reading labels: %v", err)
	}

	limit := getUserInput()

	inputJobs, err := readInputCSV(inputFile)
	if err != nil {
		log.Fatalf("Error reading input CSV file: %v", err)
	}

	// İşlenecek toplam satır sayısını belirle
	totalJobs := len(inputJobs)
	if limit > 0 && limit < totalJobs {
		totalJobs = limit
	}

	csvFile, err := os.Create(outputFile)
	if err != nil {
		log.Fatalf("Error creating CSV file: %v", err)
	}
	defer csvFile.Close()

	writer := csv.NewWriter(csvFile)
	defer writer.Flush()

	writer.Write([]string{"Lemma", "POS", "Sınıflandırma"})

	// Goroutine setup
	jobs := make(chan ClassificationJob, maxWorkers*2)
	results := make(chan ClassificationJob, maxWorkers*2)
	var wg sync.WaitGroup

	// Worker pool başlat
	for i := 0; i < maxWorkers; i++ {
		wg.Add(1)
		go worker(jobs, results, labels, &wg)
	}

	// Job gönderme goroutine
	go func() {
		count := 0
		for _, jobData := range inputJobs {
			if limit > 0 && count >= limit {
				break
			}
			jobs <- jobData
			count++
		}
		close(jobs)
	}()

	// Sonuçları topla ve ilerlemeyi yazdır
	resultMap := make(map[int]ClassificationJob)
	processed := 0

	fmt.Println("\nSınıflandırma işlemi başladı...")
	go func() {
		for result := range results {
			resultMap[result.index] = result
			processed++
			// \r (carriage return) kullanarak aynı satırın üzerine yazarız
			fmt.Printf("\rİşlenen lemma sayısı: %d / %d", processed, totalJobs)
		}
	}()

	// Workers'ı bekle
	wg.Wait()
	close(results)
	fmt.Println() // İlerleme çubuğunun alt satırına geçmek için boşluk

	// Sonuçları CSV'ye yaz (Geliş sırasına göre / index sıralı)
	for i := 0; i < len(inputJobs); i++ {
		if limit > 0 && i >= limit {
			break
		}
		if result, exists := resultMap[i]; exists {
			classification := result.classification
			if result.err != nil {
				log.Printf("\nError classifying '%s': %v", result.lemma, result.err)
				classification = "Error"
			}
			writer.Write([]string{result.lemma, result.pos, classification})
		}
	}

	writer.Flush()
	fmt.Println("Sınıflandırma tamamlandı ve CSV dosyasına yazıldı!")

	fmt.Println("\nHalüsinasyon kontrolü yapılıyor...")
	err = validateAndFixClassifications(outputFile, labels)
	if err != nil {
		log.Fatalf("Error validating classifications: %v", err)
	}
	fmt.Println("Doğrulama tamamlandı!")
}
