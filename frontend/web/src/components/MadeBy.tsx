// "an OpsMill production" credit, linking to the OpsMill website.
// Logo: OpsMill_Logo_2C-KO_RGB.svg (version for dark backgrounds), from https://opsmill.com,
// file https://opsmill.com/wp-content/uploads/2025/05/OpsMill_Logo_2C-KO_RGB.svg
export function MadeBy() {
  return (
    <a className="made-by" href="https://opsmill.com" target="_blank" rel="noopener noreferrer">
      <span>an</span>
      <img src="/brand/opsmill-logo-dark-bg.svg" alt="OpsMill" width={83} height={22} />
      <span>production</span>
    </a>
  )
}
