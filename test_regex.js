// Test the regex pattern
const testClassNames = [
    'status-badge status-processing',
    'status-badge status-completed',
    'status-badge status-rejected status-old'
];

console.log('Testing regex pattern: /status-(?!badge)\\S+/g');

testClassNames.forEach(className => {
    console.log(`Original: "${className}"`);
    const result = className.replace(/status-(?!badge)\S+/g, '');
    console.log(`After regex: "${result}"`);
    console.log('---');
});
