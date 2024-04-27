// mailgun api wrapper for sending emails

async function sendEmailWithAttachments(
	from,
	to,
	subject,
	text,
	attachments = []
) {
	// create an account on mailgun to get these
	const apiKey = "";
	const domain = "";

	const formData = new FormData();
	formData.append("from", from);
	formData.append("to", to);
	formData.append("subject", subject);
	formData.append("text", text);

	for (const attachment of attachments) {
		formData.append("attachment", attachment, attachment.name);
	}

	try {
		const response = await fetch(
			`https://api.mailgun.net/v3/${domain}/messages`,
			{
				method: "POST",
				headers: {
					Authorization: `Basic ${btoa(`api:${apiKey}`)}`,
				},
				body: formData,
			}
		);

		if (!response.ok) {
			throw new Error("Failed to send email");
		}

		console.log("Email sent successfully!");
	} catch (error) {
		console.error("Error:", error);
	}
}
