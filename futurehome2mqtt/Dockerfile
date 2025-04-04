ARG BUILD_FROM
FROM $BUILD_FROM

RUN apk add --no-cache python3 py3-pip && \
    pip3 install --break-system-packages --upgrade pip

# Copy data for add-on
COPY . .

RUN pip3 install --break-system-packages --no-cache-dir -r requirements.txt
RUN chmod a+x /run.sh

CMD [ "/run.sh" ]
