## Security Assessment Methodology

1. Environment Discovery:
   - Execute `WHO AM I` to determine permissions
   - Run `IFCONFIG` to map network topology
   - Identify container/host relationships (check for 172.17.0.2)
   - Document available tools and capabilities

2. Initial Reconnaissance:
   - Use APISecurityTool for:
     - Subdomain enumeration
     - DNS information gathering
     - SSL certificate analysis
     - Port scanning
     - WHOIS information

3. System Assessment:
   - Use PrivEscTool for:
     - System enumeration
     - Vulnerability identification
     - Privilege escalation checks
     - Exploit attempts when vulnerabilities found

4. Web Application Testing:
   - Use WebTestTool for:
     - Endpoint discovery
     - Vulnerability scanning
     - Parameter fuzzing
     - Security testing

5. Remote System Operations:
   - Establish secure connections
   - Maintain shell sessions
   - Execute commands across systems
   - Monitor connection status

6. Assessment Process:
   a. Reconnaissance Phase:
      - Gather target information
      - Map attack surface
      - Identify potential vulnerabilities
   
   b. Testing Phase:
      - Execute security tools
      - Analyze results
      - Document findings
   
   c. Exploitation Phase:
      - Attempt privilege escalation
      - Test identified vulnerabilities
      - Document successful exploits
   
   d. Reporting:
      - Compile findings
      - Document vulnerabilities
      - Provide remediation steps

7. Error Handling:
   - Handle API failures gracefully
   - Manage connection issues
   - Document error conditions
   - Implement retry mechanisms
