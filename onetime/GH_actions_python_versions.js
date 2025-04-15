#!/usr/bin/env bun

/**
 * Script to reverse Python versions JSON data
 * Transforms from version-centric to platform-arch-centric structure
 */

function reverseVersionsJson(inputJson) {
  // Initialize the result object
  const result = {};
  
  // Process each version entry in the input array
  for (const versionEntry of inputJson) {
    const pythonVersion = versionEntry.version;
    
    // Process each file in the version's files array
    for (const file of versionEntry.files) {
      // Construct the key based on platform, platform_version (if exists), and arch
      let key = file.platform;
      if (file.platform_version) {
        key += `-${file.platform_version}`;
      }
      key += `-${file.arch}`;
      
      // If this key doesn't exist in the result yet, initialize it as an empty array
      if (!result[key]) {
        result[key] = [];
      }
      
      // Add the Python version to this platform/arch combination if not already present
      if (!result[key].includes(pythonVersion)) {
        result[key].push(pythonVersion);
      }
    }
  }
  
  return result;
}

// Fetch data from GitHub repo
async function fetchVersionsManifest() {
  try {
    const response = await fetch('https://raw.githubusercontent.com/actions/python-versions/main/versions-manifest.json');
    if (!response.ok) {
      throw new Error(`Failed to fetch data: ${response.status} ${response.statusText}`);
    }
    const data = await response.json();
    return data;
  } catch (error) {
    console.error('Error fetching versions manifest:', error);
    throw error;
  }
}

// Main function to process the data
async function main() {
  try {
    const inputData = await fetchVersionsManifest();
    const reversed = reverseVersionsJson(inputData);
    console.log(JSON.stringify(reversed, null, 2));
  } catch (error) {
    console.error('Error in main function:', error);
  }
}

// Execute the main function
main();
