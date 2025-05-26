#!/bin/bash

mkdir -p traceroute_results

universities=("Stanford" "MIT" "Peking" "Melbourne" "Helsinki")
ips=("128.12.0.2" "18.18.60.1" "115.27.245.13" "103.12.108.1" "83.150.107.249")

echo "Starting traceroute analysis for university networks..."
echo "Results will be saved in traceroute_results/ directory"
echo

# Loop through each university/IP pair
for i in "${!universities[@]}"; do
    university="${universities[$i]}"
    ip="${ips[$i]}"
    output_file="traceroute_results/${university}_${ip}.txt"

    echo "🌐 Tracing route to $university ($ip)..."
    echo "   Output: $output_file"

    sudo $(which python3) traceroute.py "$ip" > "$output_file" 2>&1

    if [ $? -eq 0 ]; then
        echo "   ✅ Completed successfully"
    else
        echo "   ❌ Failed (exit code: $?)"
    fi

    echo
done

echo "📊 Summary of results:"
echo "====================="
for i in "${!universities[@]}"; do
    university="${universities[$i]}"
    ip="${ips[$i]}"
    output_file="traceroute_results/${university}_${ip}.txt"

    if [ -f "$output_file" ]; then
        file_size=$(wc -l < "$output_file")
        echo "${university} ${ip}: ${file_size} lines in ${output_file}"
    else
        echo "${university} ${ip}: ❌ No output file generated"
    fi
done

echo
echo "🎉 All traceroutes completed!"
echo "Check the traceroute_results/ directory for individual results."
